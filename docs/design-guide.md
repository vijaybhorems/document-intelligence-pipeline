# Design guide: every decision, and how to defend it

This guide walks through the Document Intelligence Pipeline from Phase 0 to Phase 9.5. It is written for a beginner AI engineer who has to explain and defend the design: in a code review, a design review, or an interview.

Every number here was measured in this repository. The ADRs ([`docs/adr/`](adr/)) hold the full evidence and the phase notes ([`docs/notes/`](notes/)) hold the story. This guide is the map that connects them.

---

## How to defend any decision

Interviewers rarely ask "what did you build?" They ask **"why this and not that?"** A strong answer has six parts, and every decision below follows them:

1. **The problem**, in one sentence, in plain words.
2. **The options** you seriously considered (at least two).
3. **The evidence**: what you measured, and how sure you are of it.
4. **The decision.**
5. **The trade-off**: what you gave up. Every decision gives something up. Saying so out loud is what makes an answer credible.
6. **When you'd change your mind**: the conditions under which another option would win.

A weak answer stops at "I chose X because it's better." A strong one says "X and Y were within noise on quality, X was 11× cheaper, so I chose X; I'd revisit it if the prompt were re-tuned for Y."

---

## The one idea behind the whole project

**Decisions are made with evals, not opinions.**

Most AI projects pick a model, a parser and a prompt by intuition, then hope. This project does the opposite. It builds the measuring instrument first (Phase 2), then turns each design question into an experiment with a number at the end (decisions D1–D8).

Three habits make the measurements trustworthy. Know them well; they come up again and again.

### Habit 1: know your noise floor

Run the *same* system twice and the score changes, because LLMs aren't deterministic. In Phase 3, re-running an identical setup moved overall F1 by **1.6 points**, about as much as the differences between the strategies being compared. Any "improvement" smaller than the noise floor is not a finding.

**How to say it:** "Before comparing systems, I measured how much one system disagrees with itself. Differences smaller than that, I treat as ties."

### Habit 2: compare on the same documents, with confidence intervals

Two systems are compared on the **same contracts** (a *paired* comparison). The uncertainty comes from a **bootstrap**: resample the contracts with replacement 2,000 times, recompute the difference each time, and read off the middle 95% as a confidence interval (CI).

If the CI excludes zero, the difference is real at 95% confidence. If it straddles zero, call it "within noise".

**Example:** prompt v4 vs v1 on dev was **+1.18 F1 with a 95% CI of [+0.07, +2.38]**. Small, but real, because the interval doesn't include zero.

### Habit 3: protect the test set

The data is split once and frozen:

| Split | Contracts | Used for |
|---|---|---|
| **test** | 102 | final numbers only (Phase 10), never for decisions |
| **dev** | 80 | confirming decisions |
| **experiment** | 30 (a subset of dev) | cheap experiments |
| **smoke** | 5 (a subset of experiment) | CI and quick checks |
| **train** | 328 | prompt examples, rule design, load tests |

Looking at test results while tuning would quietly overfit your design to the test set, and your final number would lie. Even the load test (Phase 9) used train contracts, to keep test untouched.

---

## Phase 0: foundations

### Tooling: uv, ruff, pyright, pytest, pre-commit ([ADR I7](adr/I7-tooling.md))

**Problem:** a project that must run identically on a laptop, in CI and in a Docker image.

**Decision:**
- **uv:** manages the Python version, the virtual environment and a lockfile, all in one tool.
- **ruff:** linting and formatting.
- **pyright:** type checking.
- **pytest:** tests, with markers so paid tests (`llm`) and slow ones (`integration`) don't run by default.
- **pre-commit:** runs the same checks before each commit, including secret detection.

**Why it matters:** the **lockfile** (`uv.lock`) means "works on my machine" becomes "works everywhere": CI and the Docker image install exactly the same versions.

**Defend it:** "One fast tool replaces four (pyenv, pip, pip-tools, virtualenv), and the lockfile gives reproducible installs. Pyright runs in `standard` mode, not `strict`, because ML libraries are only partly typed."

### Google Cloud projects and budget alerts first

**Decision:** separate `dev` and `prod` projects, and a **budget alert before anything else**.

**Defend it:** "Cloud and LLM costs can run away silently. A budget alert is the cheapest insurance there is. Separate projects mean a mistake in dev can't touch prod, and permissions are scoped per project."

---

## Phase 1: data and gold labels

### Why CUAD

CUAD is 510 real commercial contracts (public SEC filings), labelled by legal experts for 41 categories. This project models them as **33 clause types** (present or absent, e.g. Non-Compete) plus **8 typed fields** (parties, dates, governing law, durations, the document name). Expert labels are what make "is the extraction right?" answerable.

### Gold spans from JSON, typed values from CSV

CUAD has two sources: the JSON has **exact character offsets** for the evidence, and the CSV has **normalized answers** like dates. The gold builder takes each from where it is best.

**Same normalizers for gold and predictions:** a date written "March 3, 2021" and one written "2021-03-03" must compare as equal. So both sides go through the *same* normalization code, and formatting differences can't show up as extraction errors.

### A quirk you should know: Warranty Duration is a clause

The name sounds like a duration, but the gold labels only say yes/no. So it's modelled as a clause. **Lesson:** read your data before designing your schema. Names lie.

### Multi-label stratified splits ([ADR I9](adr/I9-splits.md))

**Problem:** many clauses are rare (Source Code Escrow appears in 2.5% of contracts). A random split can leave a rare clause with **zero** examples in a small evaluation set, and then you can't measure it at all.

**Options:**
1. Random split.
2. Stratify by contract type.
3. **Multi-label iterative stratification:** balance all 41 labels at once.

**Evidence:** stratifying by type alone left 3 fields with zero examples in the experiment set.

**Decision:** option 3, seeded and frozen in `data/splits.json`, and switched before any evaluation ran, so no result was invalidated.

### The finding that shaped everything after: accuracy is the wrong metric

The average clause appears in only 21.9% of contracts. A system that always says "absent" is 78% *accurate*, and completely useless. That's why this project uses **precision and recall**, never accuracy.

---

## Phase 2: the evaluation harness

This phase builds the measuring instrument. If you understand this phase, you can defend every later decision.

### Three things to measure per field

- **Presence:** did the system find the field at all? ("There is an expiration clause.")
- **Value:** is the extracted value right? ("It expires 2024-03-02.")
- **Span:** does the quoted evidence match the expert's highlighted text?

The **headline metric** is presence for clauses and value for typed fields: the thing a user actually needs.

**Why separate them:** a system can find the right clause but get the date wrong. Mixing the two hides which part to fix.

### Precision, recall, F1 in one breath

- **Precision:** of the things the system claimed, how many were right?
- **Recall:** of the things that were there, how many did it find?
- **F1:** their harmonic mean. It is only high if both are.

**Micro vs macro:**
- **Micro F1** pools all decisions, so it reflects overall volume.
- **Macro F1** averages per-field scores, so every field counts equally, rare ones included.

### Baselines: the "is it even worth it?" check

| System | Overall F1 | What it shows |
|---|---|---|
| all_absent | 0.0 | the 78%-accurate do-nothing system scores zero |
| keyword | **55.8** | the bar an LLM must clear |

The keyword baseline reached 91% recall but only 40% precision on clauses, because words like "assign" appear everywhere. This told us the LLM's job on clauses is mostly **precision**: judging whether the text really creates the obligation.

### The phrasing slice

Recall is measured separately on contracts that use the *usual* words for a clause ("canonical") and those that don't ("non-canonical"). For the keyword baseline the gap was **28.8 points**. That gap is what an LLM should close, since understanding meaning, not matching words, is its advantage.

### The oracle test

Feed the gold labels in *as if* they were predictions, and every score must be 100%. Anything less is a bug in the scorer. It found one: spans made only of redaction marks scored 0 against themselves.

**Defend it:** "I tested the ruler before measuring with it."

---

## Phase 3: first LLM extraction

### Plain OpenAI SDK, no framework ([ADR I1](SPEC.md))

**Decision:** call the OpenAI SDK directly, with **Structured Outputs**: you give the API a Pydantic model and it guarantees JSON matching that schema.

**Defend it:** "Structured Outputs already does what a framework would add. A framework early on hides exactly the mechanics I was trying to learn: tokens, caching, costs. LlamaIndex is used only where it adds something, in the retrieval experiment."

### Quotes before answers

The output schema asks for the **evidence quote first, then the value**. The model writes left to right, so this makes it commit to the text before it answers. Every value comes with the words that justify it, which later enables grounding (Phase 4) and citations (Phase 9.5).

### D4: one call per contract ([ADR D4](adr/D4-field-grouping.md))

**Problem:** extract 41 fields. One big call, a few calls by field group, or one call per field?

**Evidence:** the three were tied on quality, within noise. Single was **3.2× cheaper than grouped and 18× cheaper than per-field**, and the fastest.

**Decision:** single call: **81.5 F1 on dev at $0.0048 per contract**, 35 of 41 fields better than the keyword baseline.

**The caching lesson** (a great interview story):
- OpenAI caches a repeated *prefix* of the prompt at a 90% discount.
- The first grouped run cached **0%**, because the cache includes the **schema**, and each group had a different one. Fix: one shared schema.
- Even then, caching within a run was only ~20%, because parallel calls land on different cache servers.
- **Lesson:** budget with the no-cache estimate.

### Cost control from day one

Every paid call is appended to a **ledger** (`usage.jsonl`) *as it happens*, not at the end of a run.

**Why:** a run crashed once and its spend went unrecorded, because usage was only written at the end. Now a crash can't hide spend. A budget guard refuses any run whose estimate exceeds what's left.

---

## Phase 4: validation and grounding

### Grounding: is the quote really in the contract?

For every quote, the system searches the contract text in steps:
1. Exact match.
2. Normalized match (whitespace, curly quotes).
3. Fuzzy match (≥ 90% similar).
4. "Spliced" match, for quotes that cross a page break or footer.

**The headline finding:** **99.9% of quotes were found**, and **0 of 274 false positives were hallucinated**. Every wrong answer quoted real text and *misread* it.

**How to say it:** "The model doesn't make things up; it over-reads. A clause that mentions exclusivity isn't necessarily an exclusivity clause. Grounding can't catch that, so the fix had to come from prompting, not validation."

### D6: where validation goes ([ADR D6](adr/D6-validation-placement.md))

**Options:**
- **A:** trust the strict schema alone.
- **B:** check afterwards and report problems.
- **C:** check afterwards, and **re-ask** the model with the specific errors when something is invalid.

**Decision:** C. It's the only option with **100% valid outputs** and no unsupported values. It costs +12% per contract, and the extra is only spent on the ~10% of contracts that need a re-ask.

### D7: what to do with an ungrounded value ([ADR D7](adr/D7-grounding-policy.md))

**Options:** drop it, or keep it with a warning.

**Evidence:** there were no hallucinations to catch, and the one value `drop` removed was **correct** (its quote crossed a redaction, so it couldn't be found verbatim).

**Decision:** **warn**. Consumers still see a `grounded` flag on every quote and can drop values themselves.

**Defend it:** "Dropping protects against a failure we never observed, and its cost is losing real answers. Warn keeps the information and gives the choice to the consumer."

### Rules come from data

The spec proposed a rule: "Cap on Liability and Uncapped Liability can't both be present." Gold data showed **21% of contracts have both**, so the rule was rejected.

**Lesson:** even "obvious" business rules must be checked against labelled data, and on the train split only.

---

## Phase 5: prompting and context

### D5: prompt strategy ([ADR D5](adr/D5-prompt-strategy.md))

**Problem:** the model over-triggers on clauses that need legal judgment.

**Options:** prompt v1 (plain field list) through v4. v4 adds:
- a definition per field;
- phrasing variants;
- worked examples, including **hard negatives** (text that *sounds* like the clause but isn't), drawn from **train only**;
- a defined-terms table.

**Evidence:** v4 beat v1 on dev by **+1.18 F1 [+0.07, +2.38]**, and **precision and recall both improved**. Hard negatives were expected to trade recall for precision; they didn't.

**Decision:** v4, at **+25% cost per contract**, from the longer instructions.

**An honest point that impresses interviewers:** each step from v1 to v4 was within noise on its own; only the full bundle was significantly better. The remaining errors come from CUAD's categories being **broader than their names** (a "success fee" counts as revenue sharing). A few example phrasings can't teach category boundaries.

### D3: full contract or retrieved chunks ([ADR D3](adr/D3-context-budget.md))

**Problem:** send the whole contract, or only the passages a retriever (LlamaIndex embeddings) thinks are relevant?

**Evidence:** retrieval saved only **11%** in cost, because 41 fields need chunks from almost everywhere. It cost **3.4–4.6 F1**, significant, because clauses hide in definitions, schedules and odd sections.

**Decision:** full context.

**Defend it:** "Losing 3–4 points to save 11% of $0.006 is a bad trade. Retrieval is for when documents don't fit the context window; ours do."

---

## Phase 6: parsers and models

### D1: how a PDF gets read ([ADR D1](adr/D1-extraction-route.md))

**Problem:** PDFs are either born-digital (they contain a text layer) or scans (images only). The options:
- **pypdf:** read the text layer.
- **Docling:** layout analysis plus OCR.
- **Multimodal:** send the PDF itself to the model, which reads the page images.

**How it was tested:** CUAD has **no** scans, so scans were **synthesized** from 30 contracts (rotation, noise, JPEG compression; seeded and reproducible). Only that makes OCR and multimodal comparable on the same gold labels.

**Evidence:**
- **On born-digital PDFs,** every route was within noise of perfect text. pypdf is free and instant, so it wins.
- **On scans,** pypdf gets 0 (there's no text).
- **Docling's OCR lost 11 points on dates** (significant). Overall F1 hid this, which is why you look per field type.
- **Multimodal on scans** matched its clean-PDF score.

**Decision:** a **hybrid route**. Read the text layer with pypdf; if more than half the pages have almost no text, send the PDF multimodally.

**Defend it:** "The text layer is free information, so use it when it exists. When it doesn't, OCR damages exactly the fields that matter most (dates), and the multimodal model doesn't."

### D2: which model ([ADR D2](adr/D2-extraction-model.md))

**Evidence on the same pipeline:**

| Model | Overall F1 | Cost per contract |
|---|---|---|
| **luna** | **83.6** | **$0.0074** |
| terra | 82.7 | $0.0819 (11×) |
| sol | 82.6 | $0.1597 (22×) |

Sol was **significantly worse on clauses**, because its precision dropped: it reads clauses even more broadly.

**Decision:** keep luna.

**The nuance to mention:** the prompt was tuned on luna, so this compares *the pipeline as built*, not the models in the abstract. A prompt re-tuned for sol might change the result.

### Pareto charts

Cost on one axis and F1 on the other. A choice is on the **Pareto frontier** if no other choice is both cheaper and better. It's the cleanest visual argument for a cost/quality decision.

---

## Phase 7: the service

### Asynchronous jobs ([I2](SPEC.md))

**Problem:** extracting a long contract takes from 15 seconds to minutes. Holding an HTTP request open that long is fragile.

**Decision:**
- `POST /v1/extractions` returns **202 Accepted** with a job ID right away. The client polls a status URL.
- `?wait=true` (capped at 60 s) is a convenience for small documents.

**Defend it:** "This is the standard pattern for long work: accept, queue, poll. It survives timeouts, retries and restarts, and the queue can rate-limit the expensive part."

### Idempotency: two kinds

- **Content dedupe:** the same file (same SHA-256 hash) under the same pipeline version returns the existing result for free.
  - **Why the pipeline version is part of the key:** after a prompt or model change, the old result is no longer "the same answer", so it shouldn't be reused.
- **`Idempotency-Key` header:** a client retrying after a network error gets the same job instead of a duplicate. The same key with a *different* file is rejected with **409 Conflict**.

### Retries without double-processing

- **The rule:** a job gets 3 attempts. A failure before the last attempt answers 5xx, so the queue retries. The last failure marks the job `failed` and answers 200, so the queue stops.
- **Idempotent processing:** a finished job is left alone, so a duplicate delivery is harmless.

**Why idempotency matters:** queues deliver *at least once*, never "exactly once". Your code must be safe to run twice.

### One codebase, two backends

- **local:** files on disk, jobs in memory, an in-process queue. For tests and development.
- **gcp:** GCS, Firestore, Cloud Tasks.

docker compose runs the gcp code path against **emulators**, so the same code is tested locally that runs in the cloud.

### Errors as RFC 9457 problem details

Every error has the same JSON shape (`type`, `title`, `status`, `detail`), so clients handle all errors one way.

---

## Phase 8: deploying to Google Cloud

### Terraform, and who runs it ([ADR I10](adr/I10-deploy-responsibility.md))

**Problem:** infrastructure as code is a given; the question is *who* applies it.

**Options:** CI applies Terraform on every merge, or a person applies Terraform and CI only ships images.

**Decision:** a person applies Terraform. CI (GitHub Actions) can only push an image and update the Cloud Run services.

**Defend it:** "The repository is public. An identity that can apply Terraform can rewrite IAM and secrets. If the CI identity leaks, the damage should be 'a bad image in dev', not 'someone owns the project'."

### No stored keys: Workload Identity Federation

- **How it works:** GitHub Actions proves who it is with a short-lived **OIDC token**, which Google exchanges for a short-lived Google token. No JSON key file exists to leak or rotate.
- **The guard:** the trust is pinned to this repository's **numeric ID**, its name, and the `main` branch. In a public repo, that condition is what stops a fork from asking for credentials.

### Least privilege: one service account per job

| Account | Can do |
|---|---|
| `sa-api` | upload documents, read records, enqueue |
| `sa-worker` | read uploads, write records, read the OpenAI key |
| `sa-tasks-invoker` | call the worker, and nothing else |
| `sa-deployer` | push images, update services |

**Defend it:** "If one is compromised, the blast radius is that one job's permissions."

### The worker is private, and checked twice

The worker has internal-only ingress, and only the tasks-invoker account may call it. The app *also* verifies the Cloud Tasks OIDC token itself: **defence in depth**. If one layer is misconfigured, the other still holds.

### Secrets never touch Terraform state

Terraform creates **empty** secrets; a script pipes the values in. Terraform state is a file, and anything in it is readable by whoever can read that file.

### Things learned only by deploying

- **IAM is eventually consistent:** a new permission took ~90 s to apply, and the queue's retries covered it.
- **Cloud Run reserves `/healthz`:** Google's own front end answers some paths ending in `z`, so the health route became `/health`.
- **Cold starts were twice as slow as necessary:** LlamaIndex was imported at startup though only the retrieval experiment uses it. A test now fails if heavy libraries creep back into startup.

---

## Phase 9: analytics and hardening

### The lakehouse pattern ([I5](SPEC.md))

- **Records are the source of truth** (one JSON file each).
- **The analytics copy is derived:** an hourly job compacts records into **Parquet**, a columnar format that's fast for analytics. DuckDB queries the Parquet straight from cloud storage.
- **Compaction is incremental:** only day partitions with new records are rebuilt.
- **A layout version** forces a full rebuild when a table's columns change. This guard was added after a missing column broke search in Phase 9.5.

**Defend it:** "JSON is easy to write one at a time; Parquet is fast to scan in bulk. Keep the JSON as the truth and treat the lake as a rebuildable cache. If the lake is wrong, delete it and recompact."

### Analytics without SQL injection

The API never accepts SQL. Callers pick a **named query** and pass parameters that are checked for type, range or pattern, then **bound** by DuckDB (never pasted into the SQL text). On top of that, the DuckDB connection is **locked** so it can't read anything outside the lake, and the lock itself can't be lifted.

**DuckDB reads GCS with a short-lived token** from the service's own identity, not long-lived HMAC keys. That's the same "no stored keys" principle as Phase 8.

### Backpressure: two layers

- **At dispatch:** Cloud Tasks sends at most 4 jobs at once, which protects the OpenAI rate limit.
- **At admission:** above 200 waiting jobs, uploads get **429 Too Many Requests** with `Retry-After`. This keeps the backlog bounded instead of silently queueing hours of work.

### The sweeper, and why its number is a correctness constraint

**Problem:** a job can get stranded if every delivery fails before reaching the app.

**Decision:** a job every 10 minutes re-sends jobs idle for more than **35 minutes**, at most twice.

**Why 35:** Cloud Tasks' retry window is 30 minutes. If the sweeper re-sent a job the queue was still retrying, two workers would extract the same contract and both would be billed. So the threshold sits above the retry window and below any plausible wait, which the 429 cap keeps short.

### Load test: the numbers you can quote

50 train contracts, 10 in flight, on Cloud Run: **50/50 succeeded, $0.44 total.**

| Target | Measured |
|---|---|
| ~20-page contract, end to end, p95 under 90 s | ✅ **63 s** (mostly queue wait: 26 s waiting vs 13 s extracting, at the median) |
| Status calls, p95 under 300 ms | ✅ **160 ms** |
| Median cost per contract | **$0.0061** |

**The honest caveat:** 50 of 50 successes is consistent with a 99% success rate, but 50 samples can only *prove* at least 93% (the lower bound of a 95% interval).

### Alerts that can actually fire

Log-based metrics on `job.failed`, `sweeper.requeued` and `sweeper.gave_up`, each with an email alert.

**A bug worth telling:** the scheduled jobs logged plain text instead of JSON, so two of the three alerts could **never** have fired. It was found by reading the logs, fixed, then verified end to end by planting a fake stuck job.

**Lesson:** an alert you haven't seen fire is an assumption.

---

## Phase 9.5: agent access (MCP)

### Why expose MCP at all

Agents increasingly do the asking. MCP (Model Context Protocol) lets any MCP client (Claude Desktop, Claude Code, MCP Inspector) use the pipeline without custom integration code. The records suit agents well: every value has a quote to cite.

It is a **thin adapter**:
- REST and MCP call the same service layer (`dip.service.extractions`), so they can't diverge.
- REST stays the primary interface.

### D8: tool design ([ADR D8](adr/D8-mcp-tool-design.md))

**Problem:** few general tools (one search with every filter) or many small ones (one finder per filter)? Terse descriptions, or descriptions written for the model?

**How it was tested:**
- **Tasks:** 25 generated from gold, e.g. "Which contracts governed by Delaware law contain a change-of-control clause?"
- **Runs:** each task 3 times, with luna as the agent and only the MCP tools.
- **Two record stores:**
  - **normal:** what the pipeline extracted;
  - **oracle:** the gold labels.

**The key result:**

| Records | Answer accuracy |
|---|---|
| Ours | 64% |
| Gold | **93%** |

The 29-point gap [13, 47] is extraction, not tools: 7 of 9 failing tasks fail **only** with our records. Within that:
- **Descriptions:** v2 descriptions raised **citation accuracy by 8 points** [3, 15].
- **Granularity:** fine-grained tools cost **25–42% more** and added nothing.

**Decision:** coarse tools, v2 descriptions.

**Why the oracle run is the clever part:** without it, you'd blame the tools for errors that come from the records. The oracle comparison separates *extraction errors* from *agent errors*, so you know which part to fix.

**Honest findings:**
- **One task had wrong gold:** it asked about *automatic* renewal, but the contract allows only an extension by mutual consent, so the agents were right.
- **One agent error was real:** it joined three separate quotes into one "quote" that appears nowhere in the contract.
- **Both are written up,** not hidden.

### Authentication: Google OAuth, the server as a resource server ([ADR I8](adr/I8-mcp-authorization.md))

**How it works:**
- Google signs users in; `dip-mcp` only *checks* tokens.
- Every token goes through six checks, failing closed. Two of them do most of the work:
  - **Audience:** the token must be issued to **our** OAuth client. A valid Google token issued to any other app is rejected.
  - **Principal:** the user must be invited in our principals list, looked up by Google's stable `sub` ID, not email (emails can be reassigned).
- **If Google's token service is unreachable, the answer is 503, never a pass.**

**Why not shared API keys, as on REST?** MCP clients expect OAuth, and per-user identity enables roles, audit logs and per-user spend caps.

### SSRF: the most dangerous tool argument

**Server-side request forgery** means tricking a server into fetching a URL *for* the attacker. In the cloud, the classic target is the **metadata server** (`169.254.169.254`), which hands out the service's own credentials.

`submit_extraction` accepts a URL, so the guard:
- allows **https only**;
- resolves the hostname and requires **every** address to be public;
- connects to the **checked address** (so a second DNS answer can't swap in an internal one: "DNS rebinding");
- re-checks every redirect;
- caps the download size.

### Prompt injection, in both directions

- **Inbound:** a contract can contain "ignore previous instructions". A live test confirms extraction stays correct: Texas law, not "Mars".
- **Outbound:** returned quotes land in the *calling agent's* context. So document text appears **only** inside a capped `quote` field, described in the schema as untrusted data, never in summaries or top-level fields.

### Spend caps that hold before the bill

Each user has a daily cap. An estimated cost is **reserved** when a job is submitted, and settled with the real cost when it finishes. So a burst of submissions can't overshoot the cap while jobs are still queued.

### What the real client test taught

Connecting MCP Inspector to the deployed server surfaced four bugs no unit test caught:

1. **The SDK's DNS-rebinding protection** allows only `localhost` by default, which would block everything behind Cloud Run. It's now configured explicitly.
2. **A held-open notification stream:** the stateless server held `GET /mcp` open for 60 s, and Inspector queued every request behind it. The fix follows the MCP spec: answer **405**.
3. **A cold start just over the 30 s startup budget:** the budget is now 120 s.
4. **An outdated lake:** the compactor ran an older image, so new columns were missing. A layout version now forces a rebuild.

**Lesson:** test with a real client in the real environment, early.

---

## Phase 10: the final test

### One run per finalist on untouched data

The test set (102 contracts) was used **once per finalist**, at the very end:
- production on born-digital PDFs;
- production on synthetic scans;
- the keyword baseline.

**Results:**

| Finalist | Overall micro F1 |
|---|---|
| Production, born-digital | **84.0 [82–86]** |
| Production, scans | 82.8 |
| Keyword | 54.0 |

Production beats keyword by **+30.0 [+26.5, +34.1]**. Test agrees with dev (82.7) and experiment (83.6), the evidence that the design wasn't overfit to the sets it was tuned on.

**How to say it:** "I froze the test set before the first experiment and scored it once per finalist. The held-out number matches the tuning sets, so the gains are real, not tuned to the data."

### Small effects need big samples

Scanning cost **−0.3 (within noise) on 30 contracts** and **−1.2 [−2.3, −0.1] (significant) on 102**.

**Why it matters:** the effect didn't appear; the instrument got precise enough to see it. "Within noise" means "too small for this sample", not "zero".

### Don't fix what you found on test

The error analysis found a one-line fix worth 18 points of governing-law precision: the model adds "United States" beside a state. It was spotted in test results, so it is **not** applied to the test numbers. Re-scoring test after a fix would be tuning on test. It's the first item for the next iteration, measured on dev.

### Measured error is not all model error

Reading 50 errors by hand found **13 suspected label-noise cases**, 8 of them clear-cut, where the contract text qualifies but gold says it doesn't. So clause precision (71) is a **lower bound**. The honest move: report against gold unchanged, and say so.

---

## Cross-cutting themes (good closing answers)

**Cost:**
- **Measured, not guessed:** every paid call is ledgered as it happens, with an estimate and a budget guard before each run.
- **Final economics:** about **$0.006 per born-digital contract** in production; idle infrastructure costs about $0.50 a month (everything scales to zero).
- **The whole project's LLM spend:** about $19.20 of a $20 budget, every experiment and the final test included.

**Security:**
- **No long-lived Google credentials anywhere:** Workload Identity for CI, service-account identity for services and DuckDB. The keys that must be long-lived (OpenAI, Arize, the REST API keys) live only in Secret Manager, readable by the one service that needs each.
- **Least privilege per job,** with defence in depth on internal calls.
- **Secrets never in state or logs.**
- **Untrusted input** handled for both URLs (SSRF) and document text (injection).

**Reliability:**
- **At-least-once delivery** with idempotent processing.
- **Bounded retries,** and a sweeper for strays.
- **Backpressure** at admission and dispatch.
- **Alerts** verified by actually firing them.

**Honesty:** every ADR says what was given up and when the choice would change. Results include their confidence intervals and their noise floor. Bugs found along the way are written down, not hidden. This is the strongest signal of engineering maturity you can give.

---

## Practice questions

Answer each out loud in under a minute, then check against the section above.

1. Why not use accuracy to evaluate extraction?
2. What is a noise floor, and how did it change a decision?
3. Why compare systems on the same documents, and what does a bootstrap CI tell you?
4. Why one LLM call per contract instead of one per field?
5. Prompt caching hit 0%. Why, and what fixed it?
6. Your grounding says 99.9% of quotes are real, yet precision is ~70% on clauses. How?
7. Why warn on ungrounded values instead of dropping them?
8. Why does the full contract beat retrieval here, and when wouldn't it?
9. Why synthesize scans instead of testing OCR on CUAD?
10. Overall F1 for Docling on scans was within noise. Why reject it anyway?
11. A model 22× more expensive scored the same. Give two reasons that could be true of *this pipeline* without that model being worse in general.
12. Why does the API return 202 instead of the record?
13. What two kinds of idempotency does the service have, and what does each protect against?
14. Why must a job be safe to process twice?
15. Why does a person, not CI, apply Terraform?
16. What stops a fork of a public repo from deploying?
17. Why is the worker checked by both Cloud Run IAM and the app?
18. Why keep JSON as the truth and Parquet as a copy?
19. Explain the sweeper's 35 minutes as a constraint between two other numbers.
20. Why did fine-grained MCP tools lose, and what did the oracle run reveal?
21. Why check the token's audience if Google already signed it?
22. What is SSRF, and why does `submit_extraction` need a guard?
23. How can a contract attack the *agent* that reads your tool results?
24. Name a bug that only appeared in the real environment, and how you'd catch it earlier next time.
25. Why is the test set scored only once per finalist, and why isn't the governing-law fix in the final numbers?
26. Scanning was "within noise" on 30 contracts and significant on 102. Explain.

---

## Glossary

| Term | Meaning |
|---|---|
| **Structured Outputs** | API feature that guarantees the model's output matches a JSON schema |
| **Grounding** | checking that a quoted piece of evidence really appears in the source document |
| **Over-triggering** | reporting a clause as present when the text only resembles it |
| **Hard negative** | an example that looks like a positive but isn't; teaches the boundary |
| **Bootstrap CI** | uncertainty from resampling the evaluation set many times |
| **Paired comparison** | two systems scored on the same items, so item difficulty cancels out |
| **Noise floor** | how much an unchanged system's score varies between runs |
| **Oracle run** | the same evaluation with perfect inputs, to isolate where errors come from |
| **Pareto frontier** | the options not beaten on both cost and quality by any other |
| **Idempotent** | safe to do twice with the same result |
| **At-least-once delivery** | a queue guarantee: messages arrive, possibly more than once |
| **Backpressure** | refusing or slowing new work when the system is full |
| **OIDC token** | a signed identity token; here GitHub's, Cloud Tasks' and Google's |
| **Workload Identity Federation** | exchanging an external OIDC token for short-lived Google credentials |
| **Least privilege** | each identity gets only the permissions its job needs |
| **Lakehouse** | raw records as truth, plus a derived columnar copy for analytics |
| **SSRF** | tricking a server into making requests on an attacker's behalf |
| **Prompt injection** | text in data that tries to act as instructions to a model |
| **MCP** | Model Context Protocol, a standard way for AI agents to call tools |
| **Resource server** | a server that checks OAuth tokens issued by someone else |
