# syntax=docker/dockerfile:1
# One image for the API and the worker (SPEC §12, ADR I3); DIP_ROLE picks which app runs.
# Docling is not installed: production uses the hybrid pypdf/multimodal route (ADR D1).
#
#   docker build -f docker/Dockerfile -t dip .
#   docker run -p 8080:8080 -e DIP_ROLE=api dip
#
# Base images are pinned by digest; Dependabot (docker ecosystem) proposes bumps.

FROM ghcr.io/astral-sh/uv:0.12.10@sha256:2bb3ebca0a796a155094a27773d290c4b074572e6107f171d88d086682fd2500 AS uv

# ---------------------------------------------------------------- build
FROM python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /src

# Dependencies first, from the lockfile alone: this layer is reused until uv.lock changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project

# Then the project itself, as a regular (non-editable) install: the venv is self-contained.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

# Fail the build, not the first request, if package data didn't make it in: without
# field_notes.json the prompt silently loses its examples (decision D5).
RUN /app/.venv/bin/python -c "from dip.extract.prompts import _field_notes; assert _field_notes(), 'field_notes.json missing from the wheel'"

# DuckDB's httpfs (reads the lake on GCS) installed now, for this platform, so the API
# never downloads code at runtime. DuckDB verifies the extension's signature.
RUN /app/.venv/bin/python -c "import duckdb; duckdb.connect(config={'extension_directory': '/app/duckdb_extensions'}).install_extension('httpfs')"

# ---------------------------------------------------------------- runtime
FROM python:3.13.15-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b AS runtime
# Not "dip": Debian already has a group of that name (dial-up IP).
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
COPY --from=build --chown=root:root /app/.venv /app/.venv
COPY --from=build --chown=root:root /app/duckdb_extensions /app/duckdb_extensions
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DIP_ROLE=api \
    DIP_DUCKDB_EXTENSION_DIR=/app/duckdb_extensions \
    DIP_ENV=dev
WORKDIR /app
USER 10001:10001
EXPOSE 8080

# Cloud Run sets PORT. exec: uvicorn becomes PID 1 and gets SIGTERM for a graceful stop.
CMD ["sh", "-c", "exec uvicorn \"dip.${DIP_ROLE}.app:create_app\" --factory --host 0.0.0.0 --port \"${PORT:-8080}\" --proxy-headers --forwarded-allow-ips='*' --no-access-log"]
