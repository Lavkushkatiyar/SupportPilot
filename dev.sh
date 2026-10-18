#!/usr/bin/env bash

case "${1:-server}" in
  server)
    uv run uvicorn app.main:app --reload
    ;;

  infra)
    docker compose up -d postgres redis
    ;;
  db-shell)
    docker exec -it supportpilot-postgres psql -U postgres -d supportpilot    ;;

  lint-fix)
  ruff check . --fix
  ruff format . ;;

  *)
    echo "Usage: ./dev.sh [infra|server ]"
    exit 1
    ;;
esac    