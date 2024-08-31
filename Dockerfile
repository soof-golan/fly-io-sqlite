FROM debian:bullseye-slim

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
  apt-get update -y && apt-get install -y ca-certificates fuse3 sqlite3

COPY --from=flyio/litefs:0.5 /usr/local/bin/litefs /usr/local/bin/litefs

ENTRYPOINT litefs mount

WORKDIR /app

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

# uvicorn main:app --host 0.0.0.0 --port 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]