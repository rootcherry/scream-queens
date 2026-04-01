#!/usr/bin/env bash
#
# scripts/start_horrorverse.sh
# ------------------------------------------------------------------
# Creates tmux session "horrorverse" with:
#   project | git | api | worker | docker | client
# ------------------------------------------------------------------

set -Eeuo pipefail

SESSION="horrorverse"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

command -v tmux >/dev/null 2>&1 || { echo "tmux not installed"; exit 1; }

# docker compose detection
if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  echo "Docker Compose not found"
  exit 1
fi

cd "$PROJECT_ROOT"

# attach if exists
if tmux has-session -t "$SESSION" 2>/dev/null; then
  exec tmux attach-session -t "$SESSION"
fi

# create base session
tmux new-session -d -s "$SESSION" -n project -c "$PROJECT_ROOT"

tmux set-option -t "$SESSION" -g allow-rename off
tmux set-window-option -t "$SESSION" -g automatic-rename off

# -----------------------------
# Window 2 - git
# -----------------------------
tmux new-window -t "$SESSION" -n git -c "$PROJECT_ROOT"

# -----------------------------
# Window 3 - docker
# -----------------------------
tmux new-window -t "$SESSION" -n docker -c "$PROJECT_ROOT"

tmux send-keys -t "${SESSION}:docker" "
echo '[docker] starting containers...';
sg docker -c \"${COMPOSE_CMD} up -d\";

echo '[docker] waiting rabbitmq...';
until sg docker -c \"docker inspect -f '{{.State.Health.Status}}' horrorverse-rabbitmq 2>/dev/null\" | grep -q healthy; do sleep 1; done;

echo '[docker] rabbitmq ready ✅';
sg docker -c \"${COMPOSE_CMD} logs -f\";
" C-m

# -----------------------------
# Window 4 - worker
# -----------------------------
tmux new-window -t "$SESSION" -n worker -c "$PROJECT_ROOT"

tmux send-keys -t "${SESSION}:worker" "
echo '[worker] waiting rabbitmq...';
until sg docker -c \"docker inspect -f '{{.State.Health.Status}}' horrorverse-rabbitmq 2>/dev/null\" | grep -q healthy; do sleep 1; done;

echo '[worker] activating venv...';
source .venv/bin/activate;

echo '[worker] starting...';
python apps/worker/worker.py;
" C-m

# -----------------------------
# Window 5 - api
# -----------------------------
tmux new-window -t "$SESSION" -n api -c "$PROJECT_ROOT"

tmux send-keys -t "${SESSION}:api" "
echo '[api] waiting rabbitmq...';
until sg docker -c \"docker inspect -f '{{.State.Health.Status}}' horrorverse-rabbitmq 2>/dev/null\" | grep -q healthy; do sleep 1; done;

echo '[api] activating venv...';
source .venv/bin/activate;

echo '[api] ensuring db...';
./scripts/reset_db.sh;

echo '[api] starting...';
npm run dev;
" C-m

# -----------------------------
# Window 6 - client
# -----------------------------
tmux new-window -t "$SESSION" -n client -c "$PROJECT_ROOT"

# -----------------------------
# attach
# -----------------------------
tmux select-window -t "${SESSION}:project"
exec tmux attach-session -t "$SESSION"
