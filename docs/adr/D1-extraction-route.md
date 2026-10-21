# ADR D1: How documents reach the model

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-21 |
| **Spec ref** | SPEC §3.1 (D1), §6 |

## Context

A contract arrives as a PDF. Either a parser turns it into text for a text model, or a multimodal model reads the PDF directly. Parsers differ in cost, speed, dependencies and how they cope with scans. **All 510 CUAD PDFs are born-digital**, so each experiment-set PDF also got a **synthetic scan**: rendered to grayscale images, slightly rotated, given noise and JPEG artefacts, and rebuilt with no text layer. Scans are seeded and byte-reproducible (`dip make-scans`).

## Options considered

| Route | What it is | Dependencies |
|---|---|---|
| **pypdf** | the PDF's embedded text layer | tiny, pure Python |
| **Docling** | layout-aware parsing, RapidOCR on image regions | PyTorch + ONNX + ~600 MB of models; ~2.1 s/page OCR on Apple Silicon |
| **multimodal** | the PDF goes to the model as a file input (page images + text layer) | none locally |
| CUAD txt | the dataset's own text files: an upper bound, not a production option | |

LlamaParse was considered and skipped (separate paid account). The `Parser` interface keeps adding it small.

## Evidence

gpt-5.6-luna, prompt v4, one call per contract, experiment set (30 contracts, 533 pages). Cost = API spend + parsing time priced at **Cloud Run** rates ($0.000116/s for the 4 vCPU / 8 GiB worker, from the Cloud Billing Catalog API). The chart is [`docs/img/d1-d2-pareto.png`](../img/d1-d2-pareto.png).

![Cost vs F1, clean and scanned](../img/d1-d2-pareto.png)

| Variant | Route | $/contract | Overall F1 [95% CI] | Date F1 |
|---|---|---|---|---|
| clean | CUAD txt | 0.0060 | 83.6 [82–86] (2 runs) | 89.2 |
| clean | **pypdf** | 0.0075 | **83.6** [81–86] | 89.8 |
| clean | Docling | 0.0074 | 82.9 [80–85] | 90.5 |
| clean | multimodal | 0.0108 | 83.3 [81–86] | 88.9 |
| scanned | pypdf | 0.0024 | **0.0**: no text layer | 0.0 |
| scanned | Docling (OCR) | 0.0114 | 81.5 [79–84] | **79.3** |
| scanned | **multimodal** | 0.0153 | **83.0** [80–86] | **86.6** |

Paired bootstraps (2,000 resamples):

| Comparison | Overall Δ [CI] | Dates Δ [CI] |
|---|---|---|
| clean: pypdf − txt | +0.03 [−1.6, +1.6] | +0.6 |
| clean: Docling − txt | −0.70 [−2.3, +0.7] | +1.3 |
| clean: multimodal − pypdf | −0.29 [−2.1, +1.3] | −0.9 |
| scanned: multimodal − Docling | +1.52 [−1.0, +4.2] | +7.3 [−0.5, +15.9] |
| **Docling: scanned − clean** | −1.37 [−3.2, +0.4] | **−11.1 [−20.0, −3.1]** |
| multimodal: scanned − clean | −0.29 [−2.3, +1.5] | −2.3 [−6.7, +2.7] |

Measured costs:
- **Multimodal input:** about 1,600 tokens per clean page and about 3,200 per scanned page.
- **Docling OCR:** 1,144 s for 533 pages, about $0.0044 per contract at Cloud Run rates.
- **Latency:** multimodal p50 18–19 s against 15–17 s for the text routes.

## What we learned

1. **On born-digital PDFs the route doesn't matter for quality.** Every route is within noise of the perfect-text upper bound, so cost and simplicity decide.
2. **OCR damages exactly the fields that matter most.** Docling on scans lost 11 points on dates (digits and day/month order), significant at 95%, while overall F1 moved within noise.
3. **Multimodal shrugs off scanning.** Clean and scanned are within noise of each other, dates included. The model reads the page image itself, with no OCR step to corrupt it.
4. **A text layer is free information.** pypdf costs nothing to parse, but it has nothing to return on a scan. Hence routing.
5. **Two infrastructure bugs** surfaced while running this. Both were fixed and both are tested:
   - Docling silently skipped OCR (`onnxruntime` missing), and the parse cache stored the empty text as a real result. The parser now fails loudly.
   - Pillow's PDF timestamp made scans non-reproducible, which caused a flaky test.

## Decision

**Hybrid route:** read the text layer with **pypdf**. If more than half the pages have almost no text, send the PDF to the model **multimodally**; otherwise extract from the pypdf text (`--route hybrid`, `dip.extract.routes.HybridRoute`).
- Routing decisions were 60/60 correct on the experiment set (clean and scanned).
- On all 510 real CUAD PDFs, every contract takes the text route.
- Expected cost is about **$0.0075 per born-digital contract and about $0.015 per scanned one**, at full quality on both.

## Consequences

- **The production worker doesn't need Docling.** That drops PyTorch, ONNX and about 600 MB of models from the image, along with the 4 vCPU / 8 GiB sizing that ADR I3 assumed. The worker can be as slim as the API. Docling stays in the dev dependencies and as an option.
- Scanned contracts cost about 2× and take about 15–20% longer (p50 about 19 s vs 15–17 s). That's acceptable at these volumes; revisit if scans dominate traffic.
- Grounding on the multimodal route has no source text to check against for scans. Phase 7 should ground those quotes against a pypdf/OCR text when available, or report grounding as `unavailable` (SPEC §6.2), never silently "grounded".
- The Docling cost here is measured on Apple Silicon. Cloud Run vCPUs are likely slower, so its real cost is probably *higher*, which strengthens this decision.

**When I'd choose differently:**
- **Very high scan volume and tight cost:** Docling plus a text model is about 25% cheaper per scanned contract, if dates are re-checked (date rules, or a targeted re-ask) to recover the OCR losses.
- **Data that must not leave our infrastructure:** page images go to the API provider. Docling OCR keeps the document local to the extraction call, though the text still goes to the LLM.
- **Partly scanned PDFs** (signed signature pages appended to a typed contract): the 50% threshold sends these to text, and the scanned pages are lost. Measure on real traffic and consider per-page routing.
- **Layout-heavy documents** (tables carrying the answer): Docling's table structure may beat a raw text layer. CUAD contracts are mostly prose, so this wasn't tested here.
