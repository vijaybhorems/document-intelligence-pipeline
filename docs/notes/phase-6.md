# Phase 6: Parser & model bake-off

**Goal (SPEC §14):** pypdf, Docling, (LlamaParse), multimodal route; synthetic scans; ≥2 models; decisions D1 and D2.
**Done when:** Pareto charts exist for clean and scanned, and the D1/D2 ADRs say when I'd choose differently.

## What was built

- [x] `dip.parse`: `Parser` protocol with page spans; **pypdf** (text layer) and **Docling** (layout + RapidOCR, pinned). Parse cache keyed by content hash + parser version.
- [x] `dip make-scans`: seeded, byte-reproducible synthetic scans (rotation, noise, JPEG), with no text layer.
- [x] Routes: `--route txt|pypdf|docling|multimodal|hybrid` × `--variant clean|scanned`. Multimodal sends the PDF as a Responses API file input.
- [x] **HybridRoute** (the D1 decision): pypdf text for born-digital PDFs, multimodal for scans.
- [x] Parsing time priced at **Cloud Run** rates, with prices from the Cloud Billing Catalog API, kept apart from API spend. The budget check sees through routes, and estimates count page images.
- [x] `dip pareto`: cost-vs-F1 chart, validated palette, render-checked.
- [x] [ADR D1](../adr/D1-extraction-route.md), [ADR D2](../adr/D2-extraction-model.md); reports in [`docs/results/d1/`](../results/d1/) and [`docs/results/d2/`](../results/d2/).
- [x] Tests: 254 passing, using a hand-built text PDF, fake parsers and the fake client.

![Pareto](../img/d1-d2-pareto.png)

## What I measured (experiment set, 30 contracts, 533 pages)

**D1 (luna):** on born-digital PDFs every route is within noise of perfect text (~83.5 F1), so cheap pypdf wins. On scans:
- pypdf collapses to 0;
- **Docling OCR loses 11 points on dates** (significant);
- **multimodal holds 83.0**, unaffected by scanning.

Decision: a hybrid router.

**D2 (pypdf route, prompt v4):** terra (82.7) and sol (82.6) are within noise of luna (83.6) at **11× and 22× the cost**. Sol is significantly *worse* on clauses: precision falls 68 → 64, meaning more over-triggering. Decision: keep luna.

**Spend:** $15.94 of $20 (Phase 6: $8.76, of which terra $2.46 and sol $4.79).

## Things that went wrong, and what they taught

1. **Docling's OCR silently did nothing.** RapidOCR needs `onnxruntime`, which Docling doesn't pull in. It logged an error per page, returned empty text for scans, and **my cache stored the empty results as real**. Fix: install it, and make the parser *raise* on any conversion error so nothing broken is cached. Lesson: a cache makes silent failures permanent.
2. **A flaky test was a real bug.** Pillow stamps the current time into PDFs, so scans of the same contract differed across a second boundary. That would also have broken cache keys. Fix: pinned metadata dates.
3. **A dependency conflict hid behind a misleading error.** uv reported "no torch wheels for Python 3.13 on macOS arm64". The real cause was Docling capping `typer<0.27` against this project's arbitrary `typer>=0.27.3`, which made the resolver backtrack to ancient Docling versions.
4. **Charts need looking at.** The first render squashed every working route into a sliver because one route scored 0; labels collided and minor ticks overprinted. Fixed after a visual check.
5. **The budget check had a hole.** Route wrappers weren't `OpenAIExtractor` instances, so the pre-run estimate was silently skipped. Caught before any route ran.
6. **Two shortcuts in my own process:** a patch chained after `grep … &&` silently didn't run, and an ADR claim ("40% slower") was wrong. Both were caught by re-checking against the data.

## Concepts to understand before moving on

1. Why make synthetic scans instead of evaluating OCR on CUAD as-is?
2. Docling's overall F1 on scans is within noise of multimodal's, yet the ADR rejects it. Why do dates matter more than the overall number here?
3. What does the hybrid router decide on, and what kind of real document would it get wrong?
4. Why price parsing compute separately from API spend? Which one does the budget ledger count, and why?
5. Sol is 22× the price and slightly worse. Give two reasons that could be true *of this pipeline* without sol being a worse model.
6. Which infrastructure decision (ADR I3) does D1 change, and why does that matter for Cloud Run cold starts?

## Try it yourself

```bash
uv run dip make-scans --split smoke && uv run dip parse --parser docling --split smoke --variant scanned
uv run dip estimate --split experiment --route multimodal --variant scanned
uv run dip pareto --split experiment
```

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
