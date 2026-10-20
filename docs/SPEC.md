# Document Intelligence Pipeline — Specification

| | |
|---|---|
| **Status** | Draft v0.6 |
| **Owner** | Vijay |
| **Last updated** | 2026-10-20 |
| **Target platform** | Google Cloud (Cloud Run) |

---

## 1. Summary

A service that takes messy documents in on one end and returns clean, structured records as JSON on the other. v1 targets commercial contracts (PDF, DOCX, TXT). Every extracted value carries an evidence quote that is checked against the source. Quality is measured from day one against CUAD's expert labels, with **precision and recall per field, broken down by field type**.

```
 contract.pdf ──▶ Parse / OCR ──▶ Extract (LLM) ──▶ Validate & Ground ──▶ ContractRecord (JSON)
       │                                ▲                                         │
       └──── or: multimodal model reads the document directly ─┘                    │
                                                    ┌───────────────────────────┤
                                                    ▼                           ▼
                                          DuckDB analytics store    Evals vs labeled gold set
```

### 1.1 Why this problem

Document intelligence is one of the most common workflows inside any company. The project brief cites a Gartner estimate that 70–90% of company data is unstructured: it sits in contracts, claims, invoices and other documents, and it has to become structured before anything downstream can use it. The same pipeline shape (parse → extract → validate → evaluate) carries over to invoices, claims, or any document set you already have (§2.5). Contracts are a demanding first case, because they're long, phrased inconsistently, and full of their own defined vocabulary.

### 1.2 Goals

1. **Extract the right fields.** Choose a parsing/extraction approach from several candidates, and be able to explain the choice in terms of measured performance against cost (§6).
2. **Prompts that survive messy phrasing.** The same field shows up phrased many different ways across documents, and contracts carry their own vocabulary. The prompting and context engineering must handle both, and evals must show that it does (§7).
3. **Validated, hallucination-checked output.** Every response conforms to a versioned Pydantic schema. The right fields come back in the right shape, and values the model invented are detected (§8).
4. **Every decision is made through evals.** The choice of parser, model, how much context to send, and where validation happens is each backed by an experiment and recorded in a decision log (§3).
5. **Insight, not just a score.** Per-field and per-field-type precision and recall, plus an explanation of *why* some categories are harder than others (§10).
6. **Production deployment** on Google Cloud: containerized, deployed with Terraform and CI/CD, with secrets in Secret Manager, tracing in Arize, and cost tracking (§11–§13).
7. **Portfolio-ready write-up.** The decisions, trade-offs and results are documented with charts and screenshots, so you can discuss them on a resume and in interviews (§15).
8. **Agent access (late, optional layer).** An MCP server lets AI agents submit documents, fetch grounded records, and query the analytics store, with security and cost controls built for agent callers (§12.2). It's a thin adapter over the same pipeline and never replaces the REST API.

### 1.3 Non-goals (v1)

- A UI. The API, eval reports and Arize are the interfaces. A tiny Streamlit viewer is an optional stretch goal.
- Fine-tuning models.
- Building non-contract document types. The design must allow them (§2.5, §6.6), but v1 doesn't ship them.
- Multi-tenant auth, billing, or user management.

---

## 2. Dataset

### 2.1 CUAD

**CUAD v1** (Contract Understanding Atticus Dataset): 510 commercial contracts from SEC EDGAR filings, with more than 13,000 expert annotations across **41 label categories**. Licensed CC BY 4.0. Get it from the Atticus Project site or Zenodo. A HuggingFace mirror also exists.

**Why CUAD:** it comes with labels, so you can measure from the very first run. It also contains real contracts with real variation in phrasing, length and contract type. Record this rationale in `docs/results.md` (§15).

| Artifact | Use in this project |
|---|---|
| `full_contract_pdf/` | **Primary pipeline input.** Exercises the real parsing path. |
| `full_contract_txt/` | Clean-text input. Used as a "perfect parser" upper bound and to separate parser errors from extraction errors (§10.7). |
| `CUAD_v1.json` (SQuAD format) | Gold **spans**: exact clause text per category, with character offsets into the txt. |
| `master_clauses.csv` | One row per contract. Gold span text per category plus `<Category>-Answer` columns with **normalized answers** (Yes/No, dates, durations, jurisdictions, party names). |

> **Phase 1 findings** (details in [`docs/notes/cuad-quirks.md`](notes/cuad-quirks.md) and [`cuad-dataset-profile.md`](notes/cuad-dataset-profile.md)):
> 1. The two gold sources agree on clause presence in 16,828 of 16,830 labels. For typed fields, 160 labels mark the relevant text but have no derivable value (e.g. an expiration clause with no fixed date). Typed answers include partial dates, multiple values and "perpetual".
> 2. **All 510 PDFs are born-digital**: none is image-only. An OCR comparison on them alone proves little, which is why §6.3's synthetic-scan variant is required, not optional.
> 3. Expiration and effective dates are often *computed* by the annotator ("five years from the date hereof"), so extracting them is a reasoning task.

### 2.2 The 41 categories, grouped by field type

The field type determines the output schema shape, how the eval matches predictions to gold (§10.3), and how results are rolled up in reports.

| Field type | CUAD categories | Output shape |
|---|---|---|
| **`entity_list`** | Parties | list of `{name, aliases}`, where aliases are the defined terms ("Distributor") |
| **`text`** | Document Name | string |
| **`date`** | Agreement Date, Effective Date, Expiration Date | list of partial dates (any of year/month/day may be unknown) + `perpetual` flag + raw text |
| **`duration`** | Renewal Term, Notice Period To Terminate Renewal | list of `{value, unit, successive, count}` + `perpetual` flag + raw text |
| **`jurisdiction`** | Governing Law | list of canonical jurisdictions + raw text |
| **`clause`** (presence + evidence) | Most Favored Nation, Non-Compete, Exclusivity, No-Solicit Of Customers, Competitive Restriction Exception, No-Solicit Of Employees, Non-Disparagement, Termination For Convenience, ROFR/ROFO/ROFN, Change Of Control, Anti-Assignment, Revenue/Profit Sharing, Price Restrictions, Minimum Commitment, Volume Restriction, IP Ownership Assignment, Joint IP Ownership, License Grant, Non-Transferable License, Affiliate License-Licensor, Affiliate License-Licensee, Unlimited/All-You-Can-Eat License, Irrevocable Or Perpetual License, Source Code Escrow, Post-Termination Services, Audit Rights, Uncapped Liability, Cap On Liability, Liquidated Damages, **Warranty Duration**, Insurance, Covenant Not To Sue, Third Party Beneficiary | `{present: bool, evidence: [Evidence]}` |

That is 1 + 1 + 3 + 2 + 1 + 33 = 41, matching the CUAD README's "33 Yes/No categories". **Warranty Duration is a clause:** the README gives it a duration answer format, but the gold CSV only records Yes/No. Typed fields are lists because CUAD answers can have several values (`60 days; 180 days`). Exact category spellings live in the field registry (`dip.schema.registry`).

Clause fields also get a secondary **clause family** tag (restrictive covenants, IP & licensing, termination & term, commercial terms, liability & risk) so the report can break results down at a second level. Typed fields and clause fields behave very differently, and so do clause families.

### 2.3 Splits and labeled subsets

You start with a **small labeled subset** and grow it only when you need more statistical power.

| Set | Size | Purpose | Rules |
|---|---|---|---|
| **smoke** | 5 docs | CI regression gate | Fixed. Parse outputs are cached and committed. |
| **experiment** | 30 docs | Parser, model and prompt bake-offs (§3), where each run costs money | Drawn from dev. Fixed across all experiments so results are comparable. |
| **dev** | 80 docs | Prompt iteration, error analysis | You may read individual errors. |
| **train** | 328 docs (rest of non-test) | Source of few-shot examples and phrasing variants (§7.2) | Never evaluated on. |
| **test** | 102 docs (20%) | Milestone scoring only | **Frozen.** Never read individual errors here while tuning. |

Splits use seeded **multi-label iterative stratification** over contract type *and* the presence of all 41 fields ([ADR I9](adr/I9-splits.md)). Stratifying on contract type alone left three rare clauses with zero examples in the experiment set. `data/splits.json` is committed, regenerates byte-identically from its seed, and `dip make-splits` refuses to overwrite it without `--force`. Even so, 9 clauses have fewer than 10 positives in test, so report them with CIs and rely on type and family rollups.

### 2.4 Label quality

- Before trusting the numbers, spot-check gold labels on 10 dev documents and write down the error types you see.
- During error analysis (§10.8), "gold label is wrong" is its own error category. Count it, and don't "fix" the model for it.

### 2.5 Bringing your own documents (optional extension)

The pipeline must work on any document set, not just CUAD:

- A **labeling guide** (`docs/labeling-guide.md`) defines each field, its edge cases, and what counts as "not present".
- Hand-label **20–30 documents** into the domain-schema JSON format, using either a template file or Label Studio.
- **Double-label 5 of them** and compute per-field agreement. That agreement is roughly the ceiling for model scores on those fields.
- Adding a document type means adding a field registry (§4.2). Parsing, validation and eval code must not change.

---

## 3. Decisions are made through evals

Every significant design decision is an **experiment** with a hypothesis, fixed inputs, metrics, and a written outcome. This is the core skill the project teaches. It's also what you'll be asked about in interviews.

### 3.1 Decision register

| # | Decision | Candidates | Experiment | Primary metrics | Phase |
|---|---|---|---|---|---|
| D1 | **Parser / extraction route** | pypdf (text layer only), Docling (layout + OCR), LlamaParse, **multimodal model reading the PDF directly** | §6.4 bake-off on the experiment set: clean PDFs **and** synthetic scans | per-type F1, cost/doc, p95 latency, failure rate | 6 |
| D2 | **Extraction model** | ≥1 small/cheap and ≥1 large current model (OpenAI). Optionally an Anthropic model. | Same prompts and parser, experiment set | per-type F1, cost/doc, latency | 6 |
| D3 | **How much context to send** | full document · retrieved sections only · retrieved sections + definitions | §7.4 | recall per type (especially rare clauses), input tokens/doc | 5 |
| D4 | **Field grouping** | 1 call for all 41 fields · ~5 grouped calls · 1 call per field | Experiment set | F1, cost, latency | 3 |
| D5 | **Prompt strategy** | zero-shot definitions · + phrasing variants · + few-shot from train · + defined-terms injection | §7.2–7.3, ablation one step at a time | F1 overall + **non-canonical phrasing recall** (§10.6) | 5 |
| D6 | **Where validation goes** | strict schema only · schema + post-hoc validators · post-hoc + re-ask with validation errors | §8.4 | valid-output rate, hallucination rate, precision, extra cost | 4 |
| D7 | **Grounding policy** | keep ungrounded values with a warning · drop them | §8.3 | precision vs recall trade-off per type | 4 |
| D8 | **MCP tool design** | few coarse tools · many fine-grained tools; terse vs detailed tool descriptions | §12.2.6 agent task eval | answer accuracy, citation accuracy, tool calls per task, tokens per task | 9.5 |

### 3.2 Experiment protocol

- One variable changes at a time. Everything else is pinned in a config file (`experiments/{id}.yaml`).
- Run `dip estimate` first to check token cost (§19).
- Each run writes to `eval_runs` (§10.5) and is logged as an Arize experiment.
- Report results with bootstrap CIs. A 1-point F1 difference on 30 documents is usually noise, and you should say so.
- Each decision ends with an **ADR** in `docs/adr/` that covers context, options, the results table and chart, the decision, and its consequences. These ADRs are your interview answers.

### 3.3 Infrastructure ADRs (not eval-driven, but still recorded)

| ADR | Decision | Recommendation | Rationale |
|---|---|---|---|
| I1 | Orchestration framework | **Plain OpenAI SDK** for extraction. LlamaIndex for the retrieval variant (D3). | Structured Outputs via `client.responses.parse(..., text_format=Model)` is enough on its own. Adding a framework early hides the mechanics you're trying to learn. |
| I2 | Sync vs async API | **Async jobs** (202 + polling), plus `?wait=true` for small docs | Long documents take minutes. Cloud Tasks gives retries, backoff, and rate limiting that protect the OpenAI quota. |
| I3 | Separate api/worker images | **Yes** | Docling pulls in PyTorch and model weights, so the API should stay slim and cold-start fast. |
| I4 | Job state store | **Firestore** (native mode) | Serverless, with single-document reads and writes. DuckDB isn't built for concurrent writers. |
| I5 | Analytics store | **DuckDB over Parquet in GCS** | Cloud Run disks are ephemeral. JSON records are the source of truth, compacted into Parquet that DuckDB reads. Upgrade path: MotherDuck. |
| I6 | IaC | **Terraform** | Reproducible environments, and an industry-standard skill. |
| I7 | Tooling | **uv**, ruff, pyright, pytest, pre-commit | Fast, modern, one lockfile. |
| I8 | MCP authorization server | **Google OAuth** with a pre-registered client and in-app role mapping. An OAuth proxy only if a client requires Dynamic Client Registration. | It's already part of the GCP stack, there's no auth server to operate, and users sign in with Google accounts. Google lacks registration, custom scopes and audiences, so §12.2.5 compensates with client-ID audience checks and a Firestore role table. |

---

## 4. Data model

### 4.1 Two schemas, on purpose

1. **LLM output schema** (`schema/llm.py`): what the model is asked to emit. It must satisfy OpenAI strict mode: all fields required (use `X | None` for optional), no extra properties, the supported JSON Schema subset only, and dates as strings. Keep it flat and simple.
2. **Domain schema** (`schema/domain.py`): what clients receive and what's stored. It has rich types, validators, and normalized values, and it's built from (1) by the validation layer (§8).

Mixing these two layers is the most common mistake in LLM extraction projects.

### 4.2 Field registry: the single source of truth

One table (`schema/registry.py`) defines every field once. Prompts, both schemas, the gold-label builder, eval matchers, and report groupings are all generated from it.

```python
@dataclass(frozen=True)
class FieldSpec:
    name: str                       # "governing_law"
    cuad_category: str              # "Governing Law"
    field_type: FieldType           # FieldType.JURISDICTION
    clause_family: ClauseFamily | None
    group: FieldGroup               # extraction call grouping (D4)
    definition: str                 # plain-language definition used in prompts
    canonical_cues: tuple[str, ...] # e.g. ("governed by", "governing law") — used for the phrasing slice (§10.6)
    phrasing_variants: tuple[str, ...]  # curated from TRAIN spans (§7.2)
    multi_valued: bool = False
```

### 4.3 Domain schema

Implemented in `src/dip/schema/domain.py` (Phase 1). Its shapes follow what CUAD actually contains: partial dates, multiple values per field, and parties with defined-term aliases. Gold labels (`GoldRecord`) and predictions share `ContractFields`, so the eval compares like with like.

```python
class Evidence(BaseModel):
    quote: str                       # verbatim text from the document
    char_start: int | None = None    # filled by grounding, never by the LLM
    char_end: int | None = None
    page: int | None = None
    grounded: bool | None = None     # None until grounding has run; gold spans are True
    match_score: float | None = None # 0..1

class PartialDate(BaseModel):        # "[]/[]/2020" -> year only
    year: int | None; month: int | None; day: int | None

class DateField(BaseModel):
    values: list[PartialDate] = []   # "07/31/2000; 07/[]/2000" -> two values
    perpetual: bool = False
    raw_text: str | None = None
    evidence: list[Evidence] = []

class Duration(BaseModel):
    value: float; unit: Literal["days", "weeks", "months", "years"]
    successive: bool = False         # "successive 1 year" renewals
    count: int | None = None         # "four successive 10 years" -> 4

class DurationField(BaseModel):
    values: list[Duration] = []; perpetual: bool = False
    raw_text: str | None = None; evidence: list[Evidence] = []

class Party(BaseModel):
    name: str
    aliases: list[str] = []          # defined terms, e.g. ["Distributor"]

class ClauseField(BaseModel):
    present: bool = False
    evidence: list[Evidence] = []

class ContractFields(BaseModel):     # shared by gold and predictions
    document_name: TextField; parties: PartyListField
    agreement_date: DateField; effective_date: DateField; expiration_date: DateField
    renewal_term: DurationField; notice_period_to_terminate_renewal: DurationField
    governing_law: JurisdictionField
    clauses: ClauseSet               # 33 ClauseFields; a unit test checks them against the registry

class ContractRecord(BaseModel):     # Phase 3+: what the API returns
    record_id: UUID
    document_sha256: str
    schema_version: str              # semver; bump on breaking change
    provenance: Provenance           # route/parser+version, model, prompt_version, git sha, timings, tokens, cost_usd
    fields: ContractFields
    validation_issues: list[ValidationIssue]
```

`GET /v1/schema` returns `ContractRecord.model_json_schema()`.

---

## 5. Architecture

```
                         ┌─────────────────────────── Google Cloud ────────────────────────────┐
 client ──HTTPS──▶  [api]  Cloud Run (FastAPI, slim image)                                     │
 agent  ──MCP────▶  [mcp]  Cloud Run (MCP server, Streamable HTTP) ── same services as [api]   │
                         │    POST /v1/extractions → GCS upload, Firestore job, enqueue        │
                         │    ▼                                                                 │
                         │  Cloud Tasks (rate limit + retries)                                   │
                         │    ▼                                                                 │
                         │  [worker]  Cloud Run (heavy image, Docling models baked in)          │
                         │    route = text pipeline:  parse/OCR → extract → validate            │
                         │    route = multimodal:     PDF → model directly → validate           │
                         │    │                         └──▶ OpenAI API (key in Secret Manager)   │
                         │    ▼                                                                 │
                         │  GCS: raw/ parsed/ records/ lake/         Firestore: job status       │
                         │  [compactor] Cloud Run Job → Parquet      [eval] Cloud Run Job          │
                         │  Traces + experiments ─OTel─▶ Arize       Logs ─▶ Cloud Logging         │
                         └────────────────────────────────────────────────────────────────────┘
```

`pipeline.py` is the single orchestration path that the CLI, the worker and the eval harness all call. One code path is both measured and shipped. The REST API and the MCP server both sit on a shared service layer (`services/`: submit job, get job, get record, search records, run named query). Neither interface contains business logic of its own.

---

## 6. Parsing and extraction routes

### 6.1 Two routes

1. **Text pipeline:** a parser or OCR model turns the document into text, and then a text LLM extracts fields. Cheaper per token and easy to inspect. Quality depends on the parser.
2. **Multimodal / direct:** the PDF (or page images) goes straight to a vision-capable model, which extracts the fields. This handles layout, tables and scans without a separate parser, but image tokens are expensive and harder to debug. OpenAI's API accepts PDF file inputs directly; check current size and page limits when you implement it.

The two routes behave differently and cost differently. **Choosing between them (D1) is the headline trade-off of the project.**

### 6.2 Interfaces

```python
class Parser(Protocol):
    name: str
    version: str
    def parse(self, data: bytes, mime_type: str) -> ParsedDocument: ...

class ParsedDocument(BaseModel):
    text: str                        # canonical full text (markdown-ish)
    pages: list[PageSpan]            # page → char range in `text`
    tables: list[Table]
    sections: list[Section]          # headings → char ranges (used for retrieval and definitions)
    ocr_used: bool
    parser: str
    parser_version: str
    warnings: list[str]

class ExtractionRoute(Protocol):
    name: str                        # "text:docling", "text:pypdf", "multimodal:openai-pdf"
    def run(self, doc: SourceDocument, fields: list[FieldSpec]) -> RawExtraction: ...
```

Candidate parsers: `PlainTextParser` (CUAD txt, the upper bound), `PypdfParser` (text layer only, the cheapest), `DoclingParser` (layout plus OCR), and `LlamaParseParser` (hosted, optional).

**Grounding still needs text on the multimodal route.** Ground its quotes against the best available text layer (Docling with OCR). Report grounding as `unavailable` when no text layer exists, so grounding never silently passes.

### 6.3 Synthetic scans (to make the OCR comparison meaningful)

Create a `scanned` variant of the experiment set: rasterize each PDF page to an image at about 150 DPI, optionally adding slight rotation and noise, then rebuild an image-only PDF. Scanned documents are common in the real world (claims, invoices), and this variant is where OCR and multimodal routes earn their cost. Report every D1 result for both **clean** and **scanned**.

### 6.4 Bake-off protocol (D1, D2)

- Fixed experiment set (30 docs × {clean, scanned}). Prompt version, field grouping and validation are held constant.
- **Metrics per route:** micro and macro F1 per field type, recall on clause fields, **cost per document** (parser compute + LLM tokens, with image tokens counted separately), p50/p95 latency, and failure rate.
- **Outputs:**
  - A **cost vs F1 scatter chart (Pareto frontier)** for each of clean and scanned.
  - A per-field-type heatmap of routes against F1.
  - An ADR that states the choice and *the conditions under which you'd choose differently*, e.g. "multimodal for scanned inputs, Docling + small model for born-digital".
- A **hybrid router** is a legitimate outcome: detect low text-layer coverage and send those documents to OCR or multimodal. If you pick it, evaluate the router itself.

### 6.5 Requirements

- **Cache parsed output** at `parsed/{sha256}/{parser}-{version}.json`. Experiments never re-parse.
- Limits: 25 MB and 300 pages. Above that, reject with `413`/`422`. Supported inputs are PDF, DOCX and TXT. Anything else gets `415`, and the check sniffs the MIME type rather than trusting the extension.
- **Docling on Cloud Run:** bake model weights into the image at build time. Start the worker at 4 vCPU / 8 GiB with concurrency 1–2 and tune from measurements.

### 6.6 Extensibility

`doc_type` selects a field registry and a prompt set. Nothing in the parse or validate layers is contract-specific.

---

## 7. Prompting and context engineering

Documents aren't written to a standard. The same field shows up phrased five different ways across five documents, and contracts define their own vocabulary. This section is about making extraction **survive that variation**, and **proving** it with evals.

### 7.1 Baseline prompt (prompt v1)

- **Layout for caching:** `[system instructions] [document] [field-group instructions]`. The shared prefix is reused across group calls, so OpenAI's automatic prompt caching (prefixes of 1024+ tokens) cuts cost. Verify by reading `cached_tokens` from usage.
- Field instructions come from registry `definition`s (adapted from CUAD's category definitions).
- The model must give a **verbatim quote** for every non-null or present value, and it is told: *"If the document does not contain it, return null / present=false. Do not infer."*
- **Prompts are versioned files** (`extract/prompts/v{N}/*.jinja`). Every record stores `prompt_version`.

### 7.2 Phrasing variation

- **Learning activity:** for each field, run a DuckDB query that dumps the gold spans from **train**, and read at least 20 of them. Note the different ways the same concept is expressed. For example, Governing Law appears as "governed by the laws of", "construed in accordance with", or "subject to the jurisdiction of". Anti-Assignment may never use the word "assign" at all.
- Curate 3–6 short `phrasing_variants` per field into the registry and include them in field instructions ("this clause may be phrased as…").
- **Few-shot examples** (prompt variant): 1–2 short positive spans and 1 hard negative per field group, **drawn only from train**. Drawing from dev or test leaks labels into the prompt and inflates your scores.
- These changes are measured with the **canonical vs non-canonical phrasing slice** (§10.6). The prompt is robust if non-canonical recall approaches canonical recall.

### 7.3 Domain vocabulary and defined terms

Contracts define their own terms, such as `"Licensed Products" means…` or `ABC Corp. ("Distributor")`, and then use those terms everywhere. If the model doesn't know what the terms refer to, extraction degrades.

- **Static context:** a short legal glossary for terms the categories depend on (ROFR/ROFO/ROFN, MFN, escrow, liquidated damages, change of control).
- **Dynamic context, per document:** extract the contract's **defined terms** with a regex pass (quoted capitalized terms followed by "means" or in parentheses after a name) plus the Definitions section from Docling's structure. Inject a compact `term → definition` table into the prompt ahead of the field instructions.
- Defined terms also feed the **Parties** field: party roles are usually defined terms.
- Measure defined-terms injection as its own ablation step (D5). It should help most on Parties and licensing clauses. Check whether it does.

### 7.4 Context budget (D3)

| Variant | What is sent |
|---|---|
| Full | the whole document (falls back to map-reduce over chunks above the model's context budget) |
| Retrieved | top-k sections per field group, retrieved with LlamaIndex using registry definitions + phrasing variants as queries |
| Retrieved + definitions | retrieved sections + the defined-terms table |

Retrieval usually cuts tokens sharply but **loses recall on rare, oddly-placed clauses**. Measuring how much recall it loses, per field type, is the lesson here.

### 7.5 Model configuration

`EXTRACTION_MODEL`, `temperature`, `max_output_tokens`, `timeout`, `max_retries`, `PROMPT_VERSION` and `ROUTE` all live in config (`pydantic-settings` + experiment YAML), never in code.

### 7.6 Failure handling

| Failure | Handling |
|---|---|
| Rate limit / 5xx / timeout | Exponential backoff with jitter (SDK + `tenacity`). Cloud Tasks retry is the outer layer. |
| Refusal | The group fails and the record is marked partial. The issue is recorded and the other groups continue. |
| Truncated output | Retry once with a higher token limit, then fail the group. |
| Validation failure | See §8. Invalid data is never returned. |

Job status values: `queued → parsing → extracting → validating → succeeded | partially_succeeded | failed`.

---

## 8. Schema validation and hallucination control

Validation answers three questions. Did the **right fields** come back? Are they in the **right shape**? Did the model **hallucinate** any of them?

### 8.1 Layers

| Layer | Catches | Mechanism |
|---|---|---|
| L1: Structural | missing or extra fields, wrong types | OpenAI strict Structured Outputs + Pydantic parse of the LLM schema |
| L2: Semantic | unparseable dates, impossible durations, unknown jurisdictions | normalizers (§8.2). Each failure becomes a `ValidationIssue`. |
| L3: Grounding | **hallucinated values**: quotes that aren't in the document | fuzzy quote search (§8.3) |
| L4: Consistency | values that contradict each other | rules: expiration ≥ effective, `present=true` ⇒ ≥1 evidence, and so on |

### 8.2 Normalization

- **Dates:** `dateparser`/`python-dateutil`. Phrases like "the date of last signature" become `value=None` with `raw_text` kept.
- **Durations:** "thirty (30) days" → `{30, days}`.
- **Jurisdictions:** map to a canonical list ("State of New York" → "New York").
- **Party names:** strip suffix noise for *matching only*. The original is kept for display.

### 8.3 Grounding

Search for the quote in the source text with whitespace normalization and `rapidfuzz` partial ratio, then set `grounded`, `match_score`, offsets and page. `GROUNDING_POLICY=warn|drop` (D7).

### 8.4 Where validation goes (D6)

| Option | Description | Expected trade-off |
|---|---|---|
| A | L1 only | Cheapest. Hallucinations pass through. |
| B | L1–L4 post-hoc | No extra LLM cost. Only flags or drops problems. |
| C | B + **re-ask**: send validation errors back to the model once and ask for a correction | Higher cost and latency. May recover recall lost by dropping. |

Measure all three on the experiment set: valid-output rate, **hallucination rate** (§10.4), precision, recall, and cost/doc. Pick one and write the ADR.

---

## 9. Storage and analytics

### 9.1 GCS layout

```
gs://{project}-dip-{env}/
  raw/{sha256}.{ext}
  parsed/{sha256}/{parser}-{ver}.json
  records/dt=YYYY-MM-DD/{record_id}.json      # source of truth
  lake/records/…parquet   lake/eval/runs/…parquet   lake/eval/field_results/…parquet
```

### 9.2 Tables

- `records`: one row per record.
- `record_fields`: long format, one row per (record, field), with `field_type`, `clause_family`, `present`, `value_text`, `value_date`, `grounded`, `evidence_count`.
- `eval_runs` and `eval_field_results` (§10.5).

### 9.3 Questions DuckDB must answer (`analytics/queries/*.sql`)

- Clause prevalence by contract type.
- Governing-law distribution.
- Cost, latency and F1 by route and by model (the D1/D2 charts come from here).
- Fields that regressed between two eval runs.

`GET /v1/analytics/{query_name}` serves a **whitelisted** set of these queries. The API never accepts raw SQL.

---

## 10. Evaluation

### 10.1 Principles

- Build the eval harness **before** the extractor, and score baselines first.
- Runs are **reproducible**: each records git SHA, the experiment config, prompt version, route, model, and split.
- Scoring is **per field**, then **per field type** (and clause family), then overall.

### 10.2 Definitions (plain language)

- **Precision:** of the fields the pipeline extracted, how many were right.
  `TP / (TP + FP)`
- **Recall:** of the fields actually present in the document, how many the pipeline extracted correctly.
  `TP / (TP + FN)`
- **F1:** the harmonic mean of the two. In contract review, **recall usually matters more**: a missed clause is worse than an extra one for a lawyer to dismiss. Always report P and R separately, not just F1.

### 10.3 Matching rules per field type

Implemented in `dip.eval.matchers` (Phase 2). Every field gets a **presence** score; typed fields also get a **value** score and clauses a **span** score.

| Field type | Match rule | Counting |
|---|---|---|
| any (presence) | pred has a value or evidence vs gold has a value or a span | TP both present. FP pred only. FN gold only. TN neither. |
| `clause` (span, strict) | each gold span matched to a predicted quote by **token Jaccard ≥ 0.5** (CUAD convention), greedy one-to-one, best pairs first. Spans with no words (redaction marks like `[●]`) compare verbatim. | unmatched preds are FP, unmatched gold are FN |
| `date` | equal on **every component gold knows**: a year-only gold date (`[]/[]/2020`) matches any predicted date in 2020, but a year-only prediction doesn't match a full gold date. `perpetual` matches `perpetual`. | **single answer**: TP if any predicted value matches any gold value (CUAD's multi-valued dates are alternatives). **Wrong value = FP + FN.** Missed = FN. Spurious = FP. |
| `duration` | same length within **2%** across units (month = 365.25/12 days, year = 365.25 days), so `6 months` = `180 days` and `12 months` = `1 year`. `successive`/`count` are ignored. | single answer, as date |
| `jurisdiction` | equality after canonicalizing both sides with the Phase 1 normalizer | **set**: one-to-one matching; each value is its own TP/FP/FN |
| `entity_list` | fuzzy ratio ≥ 90 on names normalized for case, punctuation and legal suffixes (`NETGEAR, Inc.` = `Netgear Inc`) | set, as jurisdiction |
| `text` | fuzzy ratio ≥ 85 on normalized text | single answer, as date |

Unit tests cover the "wrong value = FP + FN" case. An **oracle test** scores gold against itself over all 510 contracts and must be perfect on every field and metric. It caught a real matcher bug in Phase 2.

**Typed fields are scored twice** (a Phase 1 finding). *Presence* asks whether the model found the relevant text. *Value* asks whether the normalized value is right. CUAD has 160 typed labels where the text is marked but no value can be derived, such as an expiration clause tied to an event rather than a date. These count for presence and are excluded from value scoring. So are the 26 gold answers marked `unparsed_answer`.

### 10.4 Metrics reported

- **Per field:** P, R, F1, support. TN as well for clauses.
- **Per field type and per clause family:** micro (pooled counts) and macro (mean of per-field F1). Micro is dominated by common fields and macro exposes rare ones.
- **Bootstrap 95% CIs** (resample documents, 1,000 iterations). Many rare clauses have support under 10, so the CIs stop you over-reading noise.
- **Hallucination rate:** of the predicted values whose gold is absent, the share that is also ungrounded. Also report the overall grounding rate.
- **Valid-output rate:** share of documents whose output passes L1–L2 with no errors.
- **Cost/doc, p50/p95 latency, tokens** (input / cached / output / image).
- Stretch: precision at 80% and 90% recall (CUAD's headline metric), if you have a usable confidence signal.

### 10.5 Outputs

- `eval_runs`: `run_id, created_at, git_sha, experiment_id, route, model, prompt_version, split, n_docs, config_json, totals`
- `eval_field_results`: `run_id, doc_id, field, field_type, clause_family, slice, tp, fp, fn, tn, pred_json, gold_json, error_category`
- A per-run Markdown/HTML report containing:
  - a per-type table and a per-field table sorted by F1
  - a diff against the baseline run
  - the phrasing slice (§10.6)
  - top errors per field (dev only)
- An Arize experiment for each run.

### 10.6 Phrasing robustness slice

For each field with cues, a gold-present (contract, field) is **canonical** if any gold span contains one of the registry's `canonical_cues` (matched as word prefixes), and **non-canonical** otherwise. Report presence recall on both slices. The gap measures whether your prompt survives real-world phrasing, and it's the metric that justifies the prompt work in §7.2 and §7.3.

Cues were tuned on **train only**. Parties and agreement/effective dates have none, because their spans are names or date strings, not phrasing.

### 10.7 Error attribution

- **Parser vs extractor:** the same extraction on CUAD txt vs each parser route. The F1 gap per field type is the cost of that parser.
- **Clean vs scanned:** the same route on both variants. The gap is the cost of scan quality.

### 10.8 Error analysis (at every milestone)

Manually categorize at least 50 dev errors, using `error_category` from this taxonomy:

| Category | Meaning |
|---|---|
| `parse_error` | the text was missing or garbled after parsing |
| `missed` | the text was there and the model didn't extract it |
| `wrong_value` | found the right place, normalized or read it wrong |
| `hallucinated` | value has no support in the document (ungrounded) |
| `over_trigger` | grounded quote, but the clause doesn't legally qualify |
| `normalization` | our normalizer or matcher was wrong |
| `label_noise` | the gold label is wrong |

Then write **"why these categories are hard"** in `docs/results.md`. Look for patterns such as: rare clauses with low support, clauses that require legal judgment (Uncapped Liability, Competitive Restriction Exception), dates that depend on conditions, and clauses spread across sections. This analysis is the insight interviewers look for.

### 10.9 Baselines (Phase 2)

1. **All-absent**: everything null or false. This gives the recall floor and shows how imbalanced each field is. It scores 0 F1 everywhere, yet would be **78% "accurate"** on clause presence on dev. That's why this spec uses precision and recall rather than accuracy.
2. **Regex/keyword**: canonical cues + date regexes. The LLM must beat it, and per field it's often surprisingly competitive.

**Dev results** ([`docs/results/baseline-keyword-dev.md`](results/baseline-keyword-dev.md)): headline micro F1 **55.8** (95% CI 52–59), macro 53.0.
- Clauses: P 39.6 / R 91.1, so it finds almost everything but over-triggers.
- Expiration date value F1: 14.0. These dates are mostly computed, not written in the text.
- Phrasing slice: canonical recall 86.1 vs non-canonical 57.3, a gap of 28.8 points.

### 10.10 Gold-label builder

`ingest/build_gold.py` converts CUAD into `gold/{doc_id}.json` in the domain schema, using the `-Answer` columns for typed fields and `CUAD_v1.json` spans for clauses. Unit-test it against 5 hand-checked contracts.

---

## 11. Observability

- **Logs:** structured JSON (`structlog`) with `job_id`, `record_id`, `doc_sha256` and `stage` on every line. Never log document text or keys.
- **Tracing:** OpenTelemetry + OpenInference instrumentation for OpenAI (and for LlamaIndex in the retrieval variant), exported to Arize (`arize-otel` `register(...)`; check current package names when you implement). One trace per job, with spans for `parse`, `extract.group.*`, `ground` and `validate`. Locally, send the same traces to **Arize Phoenix** in Docker, starting from the first LLM call in Phase 3.
- **Experiments:** the experiment, dev and test sets live as Arize datasets, and every eval run is an Arize experiment with per-field P/R evaluators. This is where you compare D1–D7 visually.
- **Production monitoring:** grounding rate, hallucination proxy (ungrounded rate), refusal rate, null rate per field, cost/doc, and route mix. A sudden jump in null rate is the earliest sign of a parsing regression.

---

## 12. Interfaces: REST API and MCP

The REST API (FastAPI) is the primary interface. The MCP server (§12.2) is a second, agent-facing adapter over the same service layer.

| Method & path | Description | Responses |
|---|---|---|
| `POST /v1/extractions` | multipart `file` **or** `{gcs_uri}`. Optional `?wait=true` (≤60 s) and `?route=`. `Idempotency-Key` header. | `202 {job_id, status_url}` · `200 ContractRecord` · `413/415/422` |
| `GET /v1/extractions/{job_id}` | Status, stage timings, error | `200` · `404` |
| `GET /v1/extractions/{job_id}/record` | The `ContractRecord` | `200` · `409` not finished · `404` |
| `GET /v1/schema` | JSON Schema of `ContractRecord` | `200` |
| `GET /v1/analytics/{query_name}` | Whitelisted DuckDB queries | `200` · `404` |
| `POST /internal/process` | Cloud Tasks only (OIDC) | `200` / `5xx` → retry |
| `GET /healthz`, `/readyz` | Liveness / readiness | `200` |

- **Idempotency:** the same SHA-256 + pipeline version returns the cached record unless `?force=true`.
- **Auth:** `X-API-Key` header with keys from Secret Manager. `/internal/*` accepts only the Cloud Tasks service account's OIDC token.
- **Errors:** RFC 9457 `application/problem+json`. The request size limit is enforced while streaming the upload.

### 12.1 Non-functional targets (provisional; replace with measured values after Phase 6)

| Metric | Target |
|---|---|
| p95 end-to-end, 20-page born-digital PDF | < 90 s |
| p95 latency, non-processing endpoints | < 300 ms |
| Median cost per document | set from the D1/D2 decision, then enforced in CI |
| Job success rate (valid input) | ≥ 99% |

### 12.2 MCP interface (agent access)

#### 12.2.1 Decision and rationale

**Decision: expose an MCP server, as a thin adapter added in Phase 9.5.** It isn't part of the core pipeline and it never replaces REST.

- **Agents are becoming the main users of document pipelines.** Contract questions increasingly get asked inside AI assistants and in-house agents. MCP makes the pipeline callable from any MCP client without a custom integration per client.
- **Grounded records suit agents well.** Every value has a checked quote and a page number, so an agent can cite the contract instead of guessing.
- **It's cheap to build.** It's a few hundred lines over the existing service layer (§5).
- **It's good for your portfolio.** Agent integration, and how you secured it, are strong interview topics.

**When it wouldn't be worth it:** if the only consumers are batch jobs and internal services, MCP adds attack surface for no benefit. Revisit this decision if no agent consumer exists by Phase 9.

#### 12.2.2 Transport and hosting

- Use the official **Python MCP SDK (FastMCP)** with the **Streamable HTTP** transport in **stateless mode**. No per-session server state means Cloud Run can scale out and scale to zero. Pin the SDK and MCP spec versions, and check the current SDK API when you implement it.
- Deploy as a separate Cloud Run service `dip-mcp`, using the slim api base image, its own service account, and `max-instances` set.
- **Local dev:** the stdio transport for Claude Desktop / Claude Code, plus **MCP Inspector** for manual testing.

#### 12.2.3 Tools and resources

| Tool | Input | Output | Annotations |
|---|---|---|---|
| `submit_extraction` | `document_url` (https) **or** `gcs_uri`. Optional `idempotency_key` and `wait_seconds` (≤25). | `{job_id, status, deduplicated, record_id?}` | not read-only, not destructive, idempotent (deduplicated by document hash), open-world (fetches URLs) |
| `get_extraction_status` | `job_id` | `{status, stage, started_at, error?, retry_after_s?}` | read-only |
| `get_record` | `record_id` or `job_id`, optional `fields[]` projection | `ContractRecord` (or the projected subset) with evidence | read-only |
| `search_records` | typed filters: `contract_type`, `governing_law`, `clauses_present[]`, `clauses_absent[]`, `expires_before/after`, `limit` ≤ 50, `cursor` | record summaries: `record_id`, document name, parties, key dates, and matched clauses with citations | read-only |
| `run_analytics` | `query_name` (enum of whitelisted queries) + typed params | table rows (row-capped) | read-only |

| Resource | Content |
|---|---|
| `dip://schema/contract-record` | JSON Schema of `ContractRecord` |
| `dip://fields` | Field registry: name, type, plain-language definition. This tells agents what each field means. |
| `dip://records/{record_id}` | A record, as a resource template |

**Design rules:**

- **Structured results.** Every tool declares an `outputSchema` generated from Pydantic and returns `structuredContent`, plus a one-line text summary. Tool inputs are generated from the same models, so there's one source of truth with REST.
- **Descriptions are prompts.** Tool descriptions are written for the model. They say when to use the tool, what it returns, that extraction is asynchronous and takes minutes, and how often to poll. They're versioned (`mcp/descriptions/v{N}.yaml`) and measured by D8.
- **Small responses.** Use projection, pagination, row caps, and a maximum quote length of 1,000 characters. Agents pay for every token you return.
- **Every returned value includes its evidence** (`quote`, `page`) so agents can cite it.
- **Actionable errors.** Errors come back as tool results with `isError` and an instruction for the agent, e.g. "Job still extracting; call get_extraction_status again in ~30s". Protocol-level errors are reserved for malformed requests.
- **No destructive tools.** Nothing deletes, overwrites, or re-processes records. Re-processing stays an operator action via the CLI or REST.

#### 12.2.4 Long-running jobs

Extraction takes minutes, so it can't block inside a single tool call.

- `submit_extraction` returns a `job_id` immediately. The agent polls `get_extraction_status`, guided by `retry_after_s`.
- `wait_seconds` lets small documents finish within a single call.
- If your target clients support MCP's long-running task features, adopt them, and keep polling as the fallback. Don't rely on progress notifications, because the server is stateless.

#### 12.2.5 Security

- **Authentication:** Google OAuth is the authorization server. Details are in *Authentication with Google OAuth* below. Shared static API keys are **not** accepted on MCP. Local stdio dev has no auth.
- **Least privilege:** `sa-mcp` may enqueue tasks, read records and lake data, and read its secrets. Nothing else.
- **SSRF protection on `document_url`:**
  - Allow `https` only.
  - Resolve DNS first, then block private, loopback and link-local ranges (including the metadata server `169.254.169.254`).
  - Re-check the address after redirects and cap the number of redirects.
  - Stream the download with a size cap, and sniff the content type.
  - `gcs_uri` is restricted to the project's own upload bucket.
- **Prompt injection, in both directions:**
  - Contract text is untrusted, and returned quotes land in the calling agent's context.
  - Mitigations: quotes only ever appear inside the structured `evidence.quote` field, quote length is capped, and tool descriptions state that evidence is untrusted document text and not instructions. The server never interprets document content as commands.
  - Integration tests include a fixture contract with embedded instructions ("ignore previous instructions…"). They verify that the output is plain, correctly-typed data and that extraction isn't derailed.
- **Data scope:** v1 is single-tenant, so every authorized client sees the same corpus. If more than one organization will ever connect, add `owner_id` to records and filter every query by it (§20).
- **Audit log:** every tool call is logged with principal (Google `sub` + email), tool, a hash of the arguments, result size, latency and cost. Document content is never logged.

**Authentication with Google OAuth (ADR I8)**

Google signs users in, and `dip-mcp` is an OAuth 2.1 **resource server** under the MCP authorization spec. Google's OAuth differs from a general-purpose authorization server in four ways, and the design has to account for each:

| Google behaviour | Consequence | How this spec handles it |
|---|---|---|
| No Dynamic Client Registration | MCP clients can't register themselves automatically | **Pre-register one OAuth client** (type *Web application*) in the Google Auth Platform. Give its client ID and secret to each MCP client that connects, using the client's "custom OAuth client" setting. Register each client's callback URL as an authorized redirect URI. |
| No custom scopes (only `openid`, `email`, `profile`, and Google API scopes) | `extractions:write` and similar can't be Google scopes | Request **`openid email`** only. These are non-sensitive scopes, so Google doesn't need to verify the app. **Authorization happens in-app:** a Firestore `principals` collection maps a verified Google identity to roles (`extractions:write`, `records:read`, `analytics:read`) and a daily spend cap. |
| Access tokens are opaque (not JWTs) | They can't be verified locally | Validate each bearer token with Google's **tokeninfo** endpoint. Cache the result keyed by a token hash until `min(exp, 5 min)`. |
| No resource indicators / custom audience | The token's audience is the OAuth client ID, not `dip-mcp` | Require `aud` (or `azp`) **to equal this project's client ID**. Tokens issued to any other Google client are rejected, even when they're valid Google tokens. |

**Request validation, in order (fail closed):**
1. Bearer token present. Otherwise `401` with a `WWW-Authenticate` header pointing at the protected-resource metadata.
2. tokeninfo succeeds and the token is unexpired. If tokeninfo is unreachable, return `503`. **Never** allow the request through.
3. `aud`/`azp` equals the configured client ID.
4. `email_verified == true`.
5. The principal exists in `principals` (looked up by Google `sub`, the stable ID, not by email) and isn't disabled.
6. The principal's roles include the role the called tool requires. Otherwise return a tool error naming the missing role.

**Discovery:** serve `/.well-known/oauth-protected-resource` with `authorization_servers: ["https://accounts.google.com"]`. Clients then use Google's OpenID discovery document. PKCE is required. Use the Python SDK's token-verifier hook for steps 2–6, so the auth logic is one tested module (`mcp_server/auth.py`).

**Google project setup:**
- **Consent screen:** if you're on Google Workspace, use the *Internal* audience (only your domain can sign in). Otherwise use *External* in **Testing** mode with an explicit test-user list. Test users are a second allowlist layer on top of `principals`.
- **Manual step:** the OAuth consent screen and the general-purpose OAuth client can't be fully managed by Terraform. Create them in the console and record the steps in `docs/runbook.md`.
- **Secrets:** store the client ID and secret in Secret Manager (`mcp-oauth-client-id`, `mcp-oauth-client-secret`).
- **Onboarding:** add principals with `dip principals add <email> --roles records:read,analytics:read --daily-cap-usd 5`. The command resolves and stores the `sub` on first sign-in.

**Fallback if a target MCP client requires Dynamic Client Registration:** put an OAuth proxy in front of Google, either FastMCP's Google provider or an equivalent. The proxy handles registration and the resource parameter, uses Google for login, and issues its own short-lived, audience-bound tokens. The cost is that you now operate token issuance: signing keys go in Secret Manager, client registrations go in Firestore, and every token must be short-lived. Only adopt the proxy if a required client can't use a pre-registered client ID. Record the outcome in ADR I8.

#### 12.2.6 Agent task eval (D8)

This applies "decisions through evals" to the agent layer.

- **Task set:** 20–30 scripted questions over the **dev-set** records, with gold answers derived from the gold labels. For example:
  - "Which contracts governed by New York law contain a non-compete?"
  - "When does contract X expire, and does it auto-renew?"
  - "Quote the cap-on-liability clause in contract Y."
- **Harness:** a fixed agent loop (one model, only the MCP tools available). Run each task 3 times.
- **Metrics:**
  - Answer accuracy: exact match for sets, dates and booleans. For free text, an LLM judge with a rubric, validated against 20 hand-graded answers.
  - Citation accuracy: the cited quote is grounded and comes from the right record.
  - Tool calls per task, tokens per task, and tool-use failures (wrong tool, invalid arguments, polling loops).
- **Oracle run:** run the same tasks against **gold** records loaded into the store. Comparing it with the normal run separates *extraction errors* (the record was wrong) from *agent/tool-design errors* (the record was right and the answer was wrong).
- **Variants:** tool description v1 vs v2, and coarse vs fine-grained tools. Write the results up as the D8 ADR.

#### 12.2.7 Cost and abuse controls

- Per-principal rate limit on `submit_extraction` (e.g. 10/min) and a **daily spend cap** per principal, both checked **before** enqueueing.
- Deduplicated submissions return the existing record at no cost.
- Row, page and size caps on every read tool. `max-instances` on `dip-mcp`.

#### 12.2.8 Observability

- Each tool call is an OTel span (tool, principal, latency, result bytes, `isError`), linked to the extraction trace through `job_id`.
- Monitor in Arize: tool error rate, calls per session, poll counts per job, and spend per principal.

---

## 13. Deployment and operations (Google Cloud)

- **Environments:** `dev` and `prod` as separate GCP projects. Locally, `docker compose` runs api + worker + Phoenix + the Firestore emulator + `fake-gcs-server`.
- **Terraform (`infra/`):**
  - Artifact Registry.
  - Cloud Run services `dip-api`, `dip-worker` and `dip-mcp` (Phase 9.5). Cloud Run Jobs `dip-compactor` and `dip-eval`. Cloud Scheduler.
  - Cloud Tasks queue, with dispatch rate and concurrency sized to your OpenAI limits.
  - GCS bucket (uniform access, lifecycle rules), Firestore, and Secret Manager (`openai-api-key`, `arize-api-key`, `arize-space-id`, `api-keys`).
  - Least-privilege service accounts (`sa-api`, `sa-worker`, `sa-tasks-invoker`, `sa-mcp`).
  - Google OAuth for `dip-mcp`: the consent screen and OAuth client are created manually (§12.2.5, documented in the runbook). Terraform manages the Secret Manager entries for the client ID and secret, and the Firestore `principals` collection's indexes.
  - **Budget alert** (set it up first).
  - Terraform state in GCS.
- **Containers:** multi-stage builds with `uv`, a non-root user, and pinned base image digests. The `api` image is slim. The `worker` image includes Docling and pre-downloaded models. Track image size and cold-start time.
- **CI/CD (GitHub Actions, Workload Identity Federation, no JSON keys):**
  - **On PR:** ruff, pyright, unit tests, schema snapshot test, docker build, and a **smoke eval** on 5 docs with cached parses. The PR fails if any field-type micro-F1 drops more than a configured threshold below the baseline.
  - **On merge:** build, push, `terraform apply` to dev, deploy, and post-deploy smoke test.
  - **Prod:** manual approval, then promote the same image digest.
- **Runbook (`docs/runbook.md`):** replay a failed job, re-extract everything with a new prompt version, roll back a Cloud Run revision, rotate keys, and respond to a budget alert.

---

## 14. Delivery plan

Each phase ends with tests passing, a note in `docs/notes/phase-N.md` (what you built, measured and learned), any ADRs, and **screenshots** of the relevant charts or Arize views saved to `docs/img/`.

| Phase | Build | Learn | Done when |
|---|---|---|---|
| **0. Foundations** | repo, uv, ruff, pyright, pytest, pre-commit, CI. GCP project + **budget alert**. | Modern Python tooling, GCP basics | CI green. Budget alert set. |
| **1. Data & gold** | CUAD download, DuckDB exploration, field registry, gold builder, splits, text-layer coverage check | DuckDB, dataset analysis, class imbalance | Gold validates against the schema. Prevalence table written up. `splits.json` committed. |
| **2. Eval harness** | matchers, scorer, bootstrap, report, phrasing slice, baselines | P/R/F1, micro vs macro, CIs | Baseline report on dev. Matcher unit tests, including wrong value = FP+FN. |
| **3. Extraction v0** | LLM schema, prompt v1, grouped Structured Outputs on CUAD txt. Phoenix tracing locally. **D4** experiment. | Structured Outputs, prompt caching, token cost | Beats the regex baseline on most fields. Cost/doc measured. D4 ADR. |
| **4. Validation** | normalizers, grounding, consistency rules, re-ask. **D6, D7** experiments. | Hallucination detection, validation placement | Hallucination and valid-output rates reported. D6/D7 ADRs. |
| **5. Prompting & context** | phrasing variants, few-shot from train, defined-terms extraction, glossary, retrieval variant. **D3, D5** ablations. | Prompt engineering, context engineering, RAG trade-offs | Non-canonical recall gap shrunk (or explained). D3/D5 ADRs. |
| **6. Parser & model bake-off** | pypdf, Docling, LlamaParse, multimodal route. Synthetic scans. ≥2 models. **D1, D2.** | OCR vs multimodal, cost/performance trade-offs | Pareto charts (clean + scanned). D1/D2 ADRs with "when I'd choose differently". |
| **7. Service** | FastAPI, job model, worker, docker compose with emulators | API design, async jobs, idempotency, Docker | Local E2E: upload PDF → poll → valid record. |
| **8. Cloud deploy** | Terraform, Cloud Run, Cloud Tasks, Firestore, Secret Manager, WIF CI/CD, Arize in prod | IaC, IAM, serverless | Live dev URL processes a CUAD PDF. No long-lived keys anywhere. |
| **9. Analytics & hardening** | compactor, DuckDB-over-GCS, analytics endpoint, load test (`locust`, 50 docs) | Lakehouse pattern, backpressure | §9.3 queries answered. NFR table filled with real numbers. |
| **9.5 MCP interface** | `services/` layer shared with REST, FastMCP server (stdio + Streamable HTTP), tools and resources, OAuth, SSRF guard, rate limits and spend caps, injection fixtures, agent task eval (**D8**), `dip-mcp` deploy | MCP, tool design for LLMs, OAuth resource servers, agent evals, SSRF | Claude Desktop (locally) and a remote MCP client (deployed) answer task-set questions with correct citations. Oracle vs normal run reported. D8 ADR. |
| **10. Final eval & write-up** | **One** test-set run per finalist config (≤3), final report, error analysis, portfolio write-up (§15) | Communicating results | `docs/results.md` complete with charts and screenshots. |

Phases 0–5 run locally on the dev and experiment sets and cost little. Run the full corpus only when a phase needs it.

---

## 15. Deliverables and portfolio

The decisions are the valuable part of this project. They belong on your resume, and they're what you'll be asked about in interviews.

### 15.1 `docs/results.md` (required)

1. **Problem and documents chosen:** why CUAD (or your own set), its size, the field types, and the class imbalance.
2. **Architecture:** a diagram plus one paragraph.
3. **Extraction trade-off (D1/D2):** the Pareto charts, the choice, and when you'd choose differently.
4. **Prompting and context engineering (D3/D5):** the ablation table and the phrasing-slice results.
5. **Schema validation (D6/D7):** where validation lives, what it catches, the hallucination rate before and after.
6. **Results:** final test-set P/R/F1 per field type with CIs, and the per-field table.
7. **What the model does well and badly:** best and worst categories, with *why* (from §10.8).
8. **Production:** the deployment diagram, cost/doc, latency, and what you'd do next.
9. **Agent access (MCP):** why you exposed it, the tool design, the security model (OAuth, SSRF, prompt injection), and D8 results, including how much of the agent error came from extraction versus tool use.

### 15.2 Screenshots to capture (`docs/img/`)

The per-field-type P/R bar chart · the per-field heatmap · the Pareto charts (clean and scanned) · an Arize trace of one document · an Arize experiment comparison · the phrasing-slice chart · a Cloud Run service page · a sample JSON record with evidence · MCP Inspector showing the tool list · an agent (e.g. Claude Desktop) answering a contract question with page citations from your server.

### 15.3 Interview questions you should be able to answer from your own data

- Why that parser/model? What did it cost per document, and what would make you switch?
- Which field types were hardest, and why? Which were easiest?
- How do you know the model isn't hallucinating? What's your hallucination rate, and how do you measure it?
- Where does validation happen, and why there?
- How did you handle phrasing variation and contract-specific vocabulary? What did it buy you, in numbers?
- How much of the error comes from parsing versus extraction?
- How would you adapt this to invoices or claims?
- Why expose MCP, and why not make it the main interface? How do you stop a malicious contract from hijacking the calling agent, or a `document_url` from reaching your metadata server?
- When an agent answered wrong, was the extraction wrong or the tool use? How do you know?

### 15.4 Resume bullet template

> Built and deployed (GCP Cloud Run) a document-intelligence pipeline converting commercial contracts into validated JSON. Chose *[route/model]* after a cost/accuracy bake-off of *N* configurations (*X*% lower cost at *Y* F1). Achieved *P/R* per field type on the CUAD test set and cut hallucinated fields from *A*% to *B*% via grounding validation.

---

## 16. Repository layout

```
document_intelligence_pipeline/
├── pyproject.toml / uv.lock
├── src/dip/
│   ├── config.py
│   ├── schema/      registry.py  llm.py  domain.py
│   ├── ingest/      cuad.py  build_gold.py  splits.py  text_layer.py  synth_scans.py
│   ├── analytics/   cuad_report.py   # renders analytics/queries/*.sql to Markdown
│   ├── parse/       base.py  pypdf_parser.py  docling_parser.py  llamaparse_parser.py  text_parser.py  cache.py
│   ├── extract/     routes.py  extractor.py  grouping.py  context.py (defined terms, glossary)  retrieval.py  prompts/v{N}/
│   ├── validate/    normalize.py  grounding.py  rules.py  reask.py
│   ├── pipeline.py
│   ├── store/       gcs.py  jobs.py  lake.py
│   ├── services/    jobs.py  records.py  analytics.py   # shared by api/ and mcp_server/
│   ├── mcp_server/  server.py  tools.py  resources.py  auth.py  url_fetch.py (SSRF guard)  descriptions/v{N}.yaml
│   ├── agent_eval/  tasks.yaml  harness.py  judge.py
│   ├── eval/        matchers.py  scorer.py  slices.py  bootstrap.py  report.py  baselines.py  charts.py
│   ├── api/  worker/  observability/
├── experiments/*.yaml
├── analytics/queries/*.sql
├── tests/  unit/  integration/  fixtures/
├── docker/  infra/terraform/  .github/workflows/  notebooks/
├── docs/   SPEC.md  adr/  notes/  img/  labeling-guide.md  runbook.md  results.md
└── data/                         # gitignored except splits.json
```

**CLI (`typer`):** `dip download-cuad`, `dip build-gold`, `dip make-scans`, `dip extract <path> --route ...`, `dip estimate --experiment ...`, `dip eval --experiment experiments/d1-docling.yaml`, `dip report <run_id> [--compare <run_id>]`, `dip principals add|disable|list` (MCP access).

---

## 17. Testing

- **Unit:** matchers (table-driven edge cases), normalizers, grounding, defined-terms extraction, registry ↔ schema consistency.
- **Snapshot:** JSON Schema snapshots of the domain and LLM schemas. A diff forces a deliberate `schema_version` bump.
- **LLM-free:** the extractor runs against a fake client that returns recorded responses. CI calls OpenAI only in the smoke eval job.
- **Integration:** API + worker against emulators.
- **MCP:**
  - Use the SDK's in-memory client to check that tool and resource listings and input/output schemas match snapshots.
  - Every tool returns schema-valid `structuredContent`.
  - SSRF guard tests: private IPs, the metadata IP, redirects to private addresses, oversized bodies.
  - Prompt-injection fixture contract.
  - Auth tests, with tokeninfo mocked: missing token (401 + `WWW-Authenticate`), expired token, valid Google token issued to a **different** client ID, `email_verified=false`, unknown principal, disabled principal, missing role, tokeninfo outage (must return 503, never allow), and correct cache expiry.
- **Eval regression:** the smoke-eval gate (§13).

---

## 18. Security

- [ ] Secrets only in Secret Manager. Least-privilege service accounts. WIF in CI.
- [ ] `/internal/*` OIDC-protected. Public endpoints need an API key.
- [ ] Upload validation: size, MIME sniffing, page count.
- [ ] Document text is **untrusted input**. The extractor has no tools, so prompt injection can only distort output, and grounding helps detect that. Note this in the threat model.
- [ ] No document content in logs. The bucket is private. Dependency and image scanning are on.
- [ ] MCP: Google OAuth (`openid email` only), client-ID audience check, fail-closed token validation, in-app roles keyed by Google `sub`, consent screen limited to Internal or Testing users, SSRF guard on `document_url`, `gcs_uri` limited to the project's bucket, no destructive tools, quote length cap, injection fixtures in CI, audit log of every tool call (§12.2.5).
- [ ] CUAD documents are public filings. Real customer documents would also need retention policies, provider data-retention settings, and region pinning.

---

## 19. Cost controls

- Budget alerts, `max-instances` on every service, and a Cloud Tasks dispatch rate cap.
- Parse cache + record cache by hash, and prompt caching via the prefix layout.
- `dip estimate` counts text tokens (`tiktoken`) and estimated image tokens for multimodal routes, multiplied by configured prices. Run it **before every experiment**.
- `dip eval --max-cost-usd X` aborts once spend exceeds the cap.
- Multimodal experiments run on the 30-doc experiment set only, never on the full corpus, unless the estimate is approved.
- MCP callers: per-principal rate limits and daily spend caps, checked before enqueueing (§12.2.7). Agent-eval runs have their own `--max-cost-usd`.

---

## 20. Open questions

1. Is there a usable confidence signal (logprobs, self-consistency) for precision@recall curves?
2. Strict span metric: Jaccard ≥ 0.5 or "pred contains gold"? Report both at first.
3. Is a hybrid router (text-layer coverage → route) worth its complexity? It depends on the D1 results.
4. Firestore vs GCS status objects (I4) at your scale?
5. Keep DOCX in v1?
6. ~~Partial gold dates~~ **Decided in Phase 2:** match on the components gold knows (§10.3).
7. MCP: do your target clients support MCP's long-running task features yet, or is polling enough? And do they all accept a pre-registered OAuth client ID, or will you need the OAuth proxy fallback (ADR I8)? (The authorization server is decided: Google OAuth.)
8. Will more than one organization ever connect via MCP? If so, add `owner_id` scoping before exposing `search_records`.

---

## 21. References

- CUAD: atticusprojectai.org/cuad. Hendrycks et al., "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review" (NeurIPS 2021 Datasets & Benchmarks)
- OpenAI Structured Outputs: developers.openai.com/api/docs/guides/structured-outputs. OpenAI file (PDF) inputs and vision docs.
- Docling: docling-project.github.io/docling · LlamaParse: developers.llamaindex.ai/llamaparse/parse · LlamaIndex
- Pydantic v2 · FastAPI · DuckDB (httpfs/GCS) · Cloud Run, Cloud Tasks, Firestore, Secret Manager
- Arize AX, Arize Phoenix, OpenInference
- Model Context Protocol: modelcontextprotocol.io (specification, including Authorization and Streamable HTTP transport) · MCP Python SDK (FastMCP) · MCP Inspector · Cloud Run guidance on hosting MCP servers
- Google Identity: OAuth 2.0 for web server apps, OpenID Connect, tokeninfo endpoint, Google Auth Platform (consent screen, audience and test users)

---

## Changelog

- **v0.6 (2026-10-20), Phase 2:**
  - Matching rules finalized and implemented: partial dates, cross-unit durations, set matching for jurisdictions and parties, and word-less spans (§10.3).
  - Oracle test added (§10.3).
  - Cue rules for the phrasing slice (§10.6).
  - Dev baseline results (§10.9).
  - Open question 6 resolved.

- **v0.5 (2026-10-19), Phase 1 findings:**
  - Warranty Duration reclassified as a clause (33 clauses + 8 typed fields).
  - Typed fields are lists, with partial dates, `perpetual` flags and party aliases (§2.2, §4.3).
  - Splits use multi-label iterative stratification with actual sizes (§2.3, ADR I9).
  - CUAD confirmed born-digital (§2.1).
  - Typed fields are scored for presence and for value (§10.3).
  - Added open question 6 on partial dates.

- **v0.4 (2026-10-17):**
  - Chose Google OAuth as the MCP authorization server (ADR I8).
  - Added a design that compensates for Google's lack of client registration, custom scopes and custom audience: pre-registered client, `aud` = client ID, Firestore role mapping keyed by `sub`, tokeninfo validation with caching, fail-closed checks.
  - Added Google project setup, the OAuth proxy fallback, auth test cases, and Terraform and security updates.
- **v0.3 (2026-10-17):**
  - Added the MCP interface (§12.2): decision and rationale, transport and hosting, tools and resources, long-running jobs, security (OAuth, SSRF, prompt injection), agent task eval with an oracle run (D8), cost controls, observability.
  - Added a shared `services/` layer (§5).
  - Added Phase 9.5, plus MCP items in infrastructure, testing, security, cost, portfolio and open questions.

- **v0.2 (2026-10-13):**
  - Added a decision register driven by evals (§3).
  - Added parser vs multimodal routes and a bake-off with synthetic scans (§6).
  - Added prompting and context engineering for phrasing variation and defined terms (§7).
  - Added validation placement as an experiment and hallucination metrics (§8, §10.4).
  - Added the phrasing robustness slice and an error taxonomy (§10.6, §10.8).
  - Added labeled-subset sizing and a bring-your-own-documents path (§2.3, §2.5).
  - Added portfolio deliverables (§15).
  - Reordered phases.
- **v0.1:** initial draft.
