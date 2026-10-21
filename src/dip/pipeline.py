"""The pipeline: one contract in, one validated record out (SPEC §5).

The worker, the CLI and the eval harness all call this one code path, so what
is measured is what ships. Steps, each reported through ``on_stage``:

1. **route** (D1): read the PDF text layer with pypdf; if most pages have
   none, send the PDF to the model (multimodal), otherwise use the text.
2. **extract** (D2, D3, D4, D5): one Structured Outputs call, prompt v4.
3. **validate** (D6, D7): ground quotes in the text (``warn``), check
   consistency rules, and re-ask once for fields with errors. A scan has no
   text to ground against, so grounding is reported as *unavailable*.
4. **record**: a ``ContractRecord`` with full provenance.
"""

import datetime as dt
import hashlib
import time
import uuid
from collections.abc import Callable
from enum import StrEnum

from dip.extract.convert import to_domain
from dip.extract.extractor import OpenAIExtractor
from dip.extract.routes import SCANNED_PAGE_SHARE, needs_vision
from dip.extract.system import SystemOutput, Usage
from dip.parse.pypdf_parser import PypdfParser
from dip.schema.domain import SCHEMA_VERSION, ContractFields, ContractRecord, Provenance
from dip.validate.reask import merge, problems_for
from dip.validate.validator import Policy, validate

PDF = "application/pdf"
TEXT = "text/plain"


class Stage(StrEnum):
    ROUTING = "routing"
    EXTRACTING = "extracting"
    VALIDATING = "validating"


class UnsupportedDocumentError(ValueError):
    pass


class Pipeline:
    def __init__(self, extractor: OpenAIExtractor, reask: bool = True) -> None:
        self.extractor = extractor
        self.reask = reask
        self._text_layer = PypdfParser()

    @property
    def version(self) -> str:
        """Changes whenever output for the same document could change: the idempotency key."""
        e = self.extractor
        return (
            f"schema{SCHEMA_VERSION}+prompt-{e.prompt_version}+{e.model}+{e.reasoning_effort}"
            f"+hybrid{SCANNED_PAGE_SHARE}+reask{int(self.reask)}"
        )

    def process(
        self,
        data: bytes,
        mime: str,
        on_stage: Callable[[Stage], None] = lambda _: None,
    ) -> ContractRecord:
        started = time.perf_counter()
        doc_id = "doc"

        on_stage(Stage.ROUTING)
        pages: int | None = None
        if mime == PDF:
            layer = self._text_layer.parse(data, "upload.pdf")
            pages = len(layer.pages)
            text: str | None = None if needs_vision(layer) else layer.text
        elif mime == TEXT:
            text = data.decode("utf-8")
        else:
            raise UnsupportedDocumentError(mime)
        route = "multimodal" if text is None else "text"

        on_stage(Stage.EXTRACTING)
        outputs = (
            self.extractor.predict_pdfs({doc_id: data})
            if text is None
            else self.extractor.predict_all({doc_id: text})
        )
        output = outputs.get(doc_id) or SystemOutput(
            fields=ContractFields(), issues=["all: extraction returned no output"]
        )
        usage = output.usage
        fields, extraction_issues = output.fields, list(output.issues)

        on_stage(Stage.VALIDATING)
        result = validate(fields, text, Policy.WARN)
        if self.reask and text is not None:
            problems = problems_for(fields, extraction_issues, result.issues)
            if problems:
                answers = self.extractor.reask({doc_id: text}, {doc_id: problems})
                if doc_id in answers:
                    llm_fields, reask_usage, reask_issues = answers[doc_id]
                    fresh, convert_issues = to_domain(llm_fields)
                    fields = merge(fields, fresh, set(problems))
                    usage = usage + reask_usage
                    # Issues the re-ask resolved are gone; keep what it reported.
                    extraction_issues = reask_issues + convert_issues
                    result = validate(fields, text, Policy.WARN)

        return ContractRecord(
            record_id=str(uuid.uuid4()),
            document_sha256=hashlib.sha256(data).hexdigest(),
            created_at=dt.datetime.now(dt.UTC),
            provenance=_provenance(self, route, pages, usage, time.perf_counter() - started),
            fields=result.fields,
            validation_issues=result.issues,
            extraction_issues=extraction_issues,
        )


def _provenance(
    pipeline: Pipeline, route: str, pages: int | None, usage: Usage, seconds: float
) -> Provenance:
    e = pipeline.extractor
    return Provenance(
        pipeline_version=pipeline.version,
        route=route,
        model=e.model,
        prompt_version=e.prompt_version,
        pages=pages,
        grounding="unavailable" if route == "multimodal" else "checked",
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cost_usd=usage.cost_usd,
        seconds=seconds,
    )
