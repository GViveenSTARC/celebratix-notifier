#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/mnt/linuxstore/scripting/celebratix-notifier"
VENV_PY="$APP_DIR/.venv/bin/python"
SCRIPT="$APP_DIR/check_resale.py"
LOG="$APP_DIR/cron.log"

# jitter: 0–20 seconds
sleep "$((RANDOM % 21))"

cd "$APP_DIR"

{
  echo "============================================================"
  echo "Run: $(date -Is)  Host: $(hostname)"
  echo "============================================================"
  "$VENV_PY" "$SCRIPT"
  echo
} >> "$LOG" 2>&1