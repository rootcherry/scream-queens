#!/usr/bin/env bash
#
# scripts/start_horrorverse.sh
# ------------------------------------------------------------------
# Creates tmux session "horrorverse" with:
#   project | git | api | worker | docker | client
# ------------------------------------------------------------------

set -Eeuo pipefail

SESSION="horrorverse"

# Resolve project root from this script location:
# scripts/start_horrorverse.sh -> project root is one directory up.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

err() { printf "ERROR: %s\n" "$*" >&2; }

# Basic safety checks
command -v tmux >/dev/null 2>&1 || { err "tmux not installed"; exit 1; }

# Choose a Compose command that exists on this machine (v2 preferred, v1 supported).
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  err "Docker Compose not found (install docker compose v2 or docker-compose v1)"
  exit 1
fi

cd "$PROJECT_ROOT"

# Attach if session already exists
if tmux has-session -t "$SESSION" 2>/dev/null; then
  exec tmux attach-session -t "$SESSION"
fi

# Create session (Window 1)
tmux new-session -d -s "$SESSION" -n project -c "$PROJECT_ROOT"

# Keep window names stable (do not auto-rename based on running command).
tmux set-option -t "$SESSION" -g allow-rename off
tmux set-window-option -t "$SESSION" -g automatic-rename off

# Window 2 - git
tmux new-window -t "$SESSION" -n git -c "$PROJECT_ROOT"

# Window 3 - api
tmux new-window -t "$SESSION" -n api -c "$PROJECT_ROOT"
tmux send-keys -t "${SESSION}:api" "npm run dev" C-m

# Window 4 - worker
tmux new-window -t "$SESSION" -n worker -c "$PROJECT_ROOT"
tmux send-keys -t "${SESSION}:worker" "source .venv/bin/activate && python src/worker/worker.py" C-m

# Window 5 - docker
tmux new-window -t "$SESSION" -n docker -c "$PROJECT_ROOT"
tmux send-keys -t "${SESSION}:docker" "${COMPOSE_CMD} up -d" C-m
tmux send-keys -t "${SESSION}:docker" "${COMPOSE_CMD} ps" C-m
tmux send-keys -t "${SESSION}:docker" "${COMPOSE_CMD} logs -f" C-m

# Window 6 - client
CLIENT_WIN_ID="$(tmux new-window -P -F '#{window_id}' -t "$SESSION" -n client -c "$PROJECT_ROOT")"
tmux rename-window -t "${SESSION}:${CLIENT_WIN_ID}" client

# Start on the "project" window (portable: doesn't depend on base-index).
tmux select-window -t "${SESSION}:project" 2>/dev/null || tmux select-window -t "${SESSION}:0"
exec tmux attach-session -t "$SESSION"
