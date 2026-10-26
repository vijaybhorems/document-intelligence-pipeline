# Phase 9.5: MCP interface

**Goal (SPEC §14):** a `services/` layer shared with REST, an MCP server (stdio + Streamable HTTP), tools and resources, OAuth, an SSRF guard, rate limits and spend caps, injection fixtures, the agent task eval (**D8**), and a `dip-mcp` deploy.
**Done when:** Claude Desktop (locally) and a remote MCP client (deployed) answer task-set questions with correct citations; the oracle vs normal run is reported; the D8 ADR is written.

## What was built

- [x] **Shared service layer** (`dip.service.extractions`): submit, dedupe, idempotency, backpressure and spend caps, record lookup, with typed errors. REST and MCP both call it, so they can't diverge.
- [x] **MCP server** (`dip.mcp_server`, MCP Python SDK 2.3, where `MCPServer` is the renamed FastMCP):
  - **Tools:** `submit_extraction`, `get_extraction_status`, `get_record` (field projection), `search_records` (every filter in one call, with a citation per matched clause), `run_analytics`. A fine-grained variant (one finder per filter) is kept for D8.
  - **Resources:** `dip://schema/contract-record`, `dip://fields`, `dip://records/{id}`.
  - **Results:** structured content plus the same JSON as text; quotes capped at 1,000 characters and described as untrusted; errors as `isError` results with the next step to take.
  - **Descriptions** are versioned prompts (`descriptions/v1.yaml`, `v2.yaml`).
  - **Audit:** one log line per call (principal, tool, argument hash, outcome, bytes, latency).
- [x] **Transports:** `dip mcp-stdio` for Claude Desktop (logs to stderr), and stateless Streamable HTTP on Cloud Run as `dip-mcp`.
- [x] **Google OAuth** ([ADR I8](../adr/I8-mcp-authorization.md)): six fail-closed checks (tokeninfo by POST, our client ID as audience, verified email, a principal bound by `sub`, roles), a 503 when Google is unreachable, and `dip principals add|list|disable`.
- [x] **SSRF-safe URL fetch:** https only; every resolved address must be public; the connection is pinned to the checked IP; each redirect is re-checked; the size is capped.
- [x] **Spend caps:** a per-principal rate limit and a daily cap. An estimate is reserved at submission and settled by the worker when the job ends.
- [x] **Prompt-injection fixtures:** inbound (a live LLM test) and outbound (quotes stay in capped evidence fields).
- [x] **Agent eval** (`dip agent-eval prepare|run`): normal and oracle stores of the 80 dev contracts, 25 tasks generated from gold, and an agent loop over an in-process MCP client. Every paid call goes to the spend ledger.
- [x] **Infra:** `infra/terraform/mcp.tf` (`sa-mcp`, the service, deployer rights), the OAuth wizard `infra/bootstrap/dip-mcp-oauth.sh`, and a 120 s startup budget for every service.
- [x] **[Design guide](../design-guide.md):** every decision from Phase 0 to here, written to be defended.
- [x] Tests: 322 → **365** (+1 live LLM test, run on demand).

## What I measured

**D8** ([ADR](../adr/D8-mcp-tool-design.md), [tables](../results/d8/README.md)): 25 tasks × 3 runs × 8 variants, **$0.43**.

| | Answer accuracy | Citation accuracy |
|---|---|---|
| Our records (coarse tools, v2 descriptions) | 64% | 90% |
| Gold records (oracle) | **93%** | 89% |

- **Oracle − ours = +29 points [13, 47].** 7 of 9 failing tasks fail only with our records. The agent is held back by extraction, not by the tools.
- **v2 descriptions raised citation accuracy by 8 points [3, 15],** at +14% tokens per task.
- **Fine-grained tools cost 25–42% more,** with no gain.

**Remote check (MCP Inspector → `dip-mcp` on Cloud Run):**
- **Auth:** Google sign-in, the principal bound on first use, and the audit log showing the caller.
- **The question:** "Delaware + change of control" returned 4 contracts: 3 dev and 1 train, all genuinely Delaware with a change-of-control finding.
- **Citations:** all 4 quotes were found verbatim (score 1.00) in the right contract.
- **One extraction error, visible and explained:** dev-42 cites real text that gold says is an assignment clause, not change of control. It's the same error D8 attributes to extraction.

**Local check (Claude Desktop over stdio):** the same question answered with citations from the 80-contract dev store.

**Spend:** $16.39 of $20 in the eval ledger, plus about $0.50 of service calls since Phase 7, which the ledger doesn't count.

## Things that went wrong, and what they taught

1. **The SDK's major version changed under the spec.** `FastMCP` is `MCPServer` in v2, its types are snake_case, and annotations moved. Reading the installed package before writing code saved a rewrite.
2. **"Summary only" text content would have starved some clients.** The MCP spec asks for structured results to be repeated as JSON in the text content. A one-line summary alone would leave clients that read only `content` with nothing. Interoperability beat the token saving.
3. **Four bugs only a real client in the real cloud could find:**
   - **DNS-rebinding protection** allows only `localhost` by default, which blocks Cloud Run. Now configured explicitly.
   - **A held-open notification stream:** the stateless server held `GET /mcp` for 60 s, and Inspector queued every request behind it. Fixed with 405, as the spec allows.
   - **A cold start (29 s) just over the 30 s startup budget:** the rollout failed. The budget is now 120 s, for every service.
   - **An outdated lake:** the compactor ran an older image, so new columns were missing and search crashed. A **lake layout version** now forces a full rebuild when columns change.
4. **The audit log said "ok" for a crash.** Only expected errors were classified. It now logs `crash`, while the client still sees only a generic message.
5. **The eval found its own bugs:**
   - **A task with wrong gold:** it asked about "automatic" renewal, but CUAD's renewal term includes optional extensions.
   - **A scorer path that flagged a real agent error:** an agent joining three quotes into one.
   - **Lesson:** inspect failures before believing aggregates.
6. **OAuth details are mostly about addresses:**
   - `localhost` vs `127.0.0.1` are different redirect URIs to Google, and different browser origins to the server.
   - The wizard's email prompt took "yes" as an address; it now validates.
   - Inspector's "refresh token" option asks Google for an `offline_access` scope that Google rejects.
7. **npm:** Inspector 2.10.0 declares two commands, so `npx` can't choose one (`npx -p … mcp-inspector`); 2.10.0 is also deprecated in favour of 2.10.1.

## Concepts to understand before moving on

1. Why is the MCP server an adapter over the service layer and not its own implementation? What would drift if it weren't?
2. Explain the oracle run. What would you have concluded about tool design without it?
3. Why check the token's audience, when Google already signed the token?
4. Walk through SSRF: what does an attacker gain from `https://169.254.169.254/…`, and which check stops it? What does pinning the IP add?
5. Prompt injection goes both ways here. Name each direction and its mitigation.
6. Why reserve spend at submission instead of counting it after the job finishes?
7. A stateless server and a notification stream: why is 405 the right answer, and what broke without it?

## Try it yourself

```bash
uv run dip agent-eval prepare                                       # free: stores + tasks
uv run dip agent-eval run --store oracle --repeats 1 --limit 5      # ~$0.004
uv run dip mcp-stdio --store data/mcp-store/normal                  # what Claude Desktop runs
npx -p @modelcontextprotocol/inspector@2.10.1 mcp-inspector         # then connect to dip-mcp
GOOGLE_CLOUD_PROJECT=dip-dev-c7a284e91f63 uv run dip principals list
```

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
