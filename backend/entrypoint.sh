#!/usr/bin/env sh
set -eu
uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-10000}"
