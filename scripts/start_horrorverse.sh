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

err() { printf "ERROR: %s\n" "$*" >&2; }

command -v tmux >/dev/null 2>&1 || { err "tmux not installed"; exit 1; }

# Choose Docker Compose command (v2 preferred, v1 supported)
if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
else
  err "Docker Compose not found (install docker-compose v1 or docker compose v2)"
  exit 1
fi

cd "$PROJECT_ROOT"

# Attach if session already exists
if tmux has-session -t "$SESSION" 2>/dev/null; then
  exec tmux attach-session -t "$SESSION"
fi

# Helper: run docker/compose in docker group (avoid /var/run/docker.sock permission issues)
docker_group_cmd() {
  # `sg` runs a command with supplementary group applied
  # shellcheck disable=SC2024
  sg docker -c "$*"
}

# Create session (Window 1)
tmux new-session -d -s "$SESSION" -n project -c "$PROJECT_ROOT"

tmux set-option -t "$SESSION" -g allow-rename off
tmux set-window-option -t "$SESSION" -g automatic-rename off

# Window 2 - git
tmux new-window -t "$SESSION" -n git -c "$PROJECT_ROOT"

# Window 3 - docker (bring infra up first)
tmux new-window -t "$SESSION" -n docker -c "$PROJECT_ROOT"
tmux send-keys -t "${SESSION}:docker" "echo '[docker] up -d' && sg docker -c \"${COMPOSE_CMD} up -d\"" C-m
tmux send-keys -t "${SESSION}:docker" "echo '[docker] ps' && sg docker -c \"${COMPOSE_CMD} ps\"" C-m

# Wait RabbitMQ healthy (runs in docker window so you can watch)
tmux send-keys -t "${SESSION}:docker" "echo '[docker] waiting rabbitmq healthy...'" C-m
tmux send-keys -t "${SESSION}:docker" "until sg docker -c \"docker inspect -f '{{.State.Health.Status}}' horrorverse-rabbitmq 2>/dev/null\" | grep -q healthy; do sleep 1; done; echo '[docker] rabbitmq healthy ✅'" C-m

# Tail logs last (after it is up)
tmux send-keys -t "${SESSION}:docker" "echo '[docker] logs -f' && sg docker -c \"${COMPOSE_CMD} logs -f\"" C-m

# Window 4 - worker (start after rabbitmq is healthy)
tmux new-window -t "$SESSION" -n worker -c "$PROJECT_ROOT"
tmux send-keys -t "${SESSION}:worker" "source .venv/bin/activate && python src/worker/worker.py" C-m

# Window 5 - api
tmux new-window -t "$SESSION" -n api -c "$PROJECT_ROOT"
tmux send-keys -t "${SESSION}:api" "npm run dev" C-m

# Window 6 - client
CLIENT_WIN_ID="$(tmux new-window -P -F '#{window_id}' -t "$SESSION" -n client -c "$PROJECT_ROOT")"
tmux rename-window -t "${SESSION}:${CLIENT_WIN_ID}" client

tmux select-window -t "${SESSION}:project" 2>/dev/null || tmux select-window -t "${SESSION}:0"
exec tmux attach-session -t "$SESSION"
