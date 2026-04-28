#!/usr/bin/env bash
set -e

URL="${URL:-http://localhost:8209/api/reviews}"

wrk -t1 -c1 -d30s "$URL"
wrk -t2 -c10 -d30s "$URL"
wrk -t4 -c100 -d30s "$URL"
