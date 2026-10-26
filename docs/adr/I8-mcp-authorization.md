# ADR I8: How MCP clients authenticate

| | |
|---|---|
| **Status** | Accepted; verified end to end with MCP Inspector (Phase 9.5) |
| **Date** | 2026-10-21 |
| **Spec ref** | SPEC §12.2.5; decision I8 |

## Context

Remote MCP clients need OAuth 2.1 (the MCP authorization spec). We have no identity system of our own, and the project lives on Google Cloud. Google's OAuth has no dynamic client registration, no custom scopes, opaque access tokens, and no resource indicators (SPEC §12.2.5 has the full table).

## Options considered

1. **Google as the authorization server, one pre-registered client.** dip-mcp is only a resource server.
2. **An OAuth proxy in front of Google** (FastMCP-style). It issues its own short-lived, audience-bound tokens and supports dynamic registration.
3. **Static API keys,** as on REST. They aren't OAuth, so most MCP clients can't use them, and the spec rules them out.

## Decision

**Option 1**, implemented in `dip.mcp_server.auth`. Six checks run in order and fail closed (tested in `tests/unit/mcp/test_auth.py`):
1. **Bearer token present:** else 401 with `WWW-Authenticate` pointing at `/.well-known/oauth-protected-resource/mcp`, which names `https://accounts.google.com` (no trailing slash: issuers are compared as exact strings).
2. **Token checked by Google's tokeninfo,** sent by **POST** so the token never appears in a URL or access log. If tokeninfo is unreachable, the answer is **503**, never a pass.
3. **`aud` or `azp` equals our client ID:** a valid Google token issued to any other app is refused.
4. **`email_verified`.**
5. **A principal exists for the Google `sub`** and isn't disabled. Principals are invited by email; the `sub` is bound on first sign-in, and an email later bound to a different `sub` is refused (reassigned addresses).
6. **Roles per tool,** from the principal: `records:read`, `analytics:read`, `extractions:write`. Plus a per-principal rate limit and a daily spend cap on `submit_extraction`, reserved before enqueueing and settled when the job ends.

Positive results are cached by token hash for at most 5 minutes, so disabling a principal takes effect within 5 minutes.

**Changed from the spec:**
- **The client secret is not stored server-side.** A resource server never needs it; only clients (Inspector, Claude) do. The client ID is public by design and lives in a gitignored tfvars file.
- **DNS-rebinding protection is configured explicitly.** The SDK's default allows only `localhost` Host headers, so behind Cloud Run every request would have been refused (421).
- **Google accepted MCP Inspector 2.10.1's authorization request as-is**, so no proxy was needed. (Whether that client sends the RFC 8707 `resource` parameter wasn't checked; if a client's request is rejected for it, that's the case for the proxy.)
- **What did need care:** redirect URIs (`localhost` and `127.0.0.1` are different to Google), browser origins (both allowed), and not requesting `offline_access` (Google rejects it).

## Consequences

- **No token issuance to operate:** no signing keys, no client registry, nothing to rotate.
- **One extra network call per new token** (tokeninfo), cached for up to 5 minutes.
- **Two allowlists:** the consent screen in Testing mode (Google's test users), and our principals.
- **When I'd choose differently:** if a required MCP client insists on dynamic client registration (MCP Inspector took a pre-registered client ID and secret in Phase 9.5; Claude's custom connectors offer the same fields), add the proxy (option 2). Or with more than one organization: add `owner_id` scoping first (SPEC §20, open question 8).
