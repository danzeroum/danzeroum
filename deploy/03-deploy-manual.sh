#!/usr/bin/env bash
# ============================================================
# 03 — Deploy MANUAL (rode LOCALMENTE). Faz o mesmo que o GitHub Actions:
# entra no VPS por SSH, atualiza o repo e sobe os containers.
#
# Uso:
#   SSH_HOST=203.0.113.10 \
#   SSH_USER=root \
#   SSH_PORT=22 \
#   APP_DIR=/opt/btv/danzeroum \
#   SSH_KEY=~/.ssh/danzeroum_deploy \
#   bash deploy/03-deploy-manual.sh
# ============================================================
set -euo pipefail

: "${SSH_HOST:?defina SSH_HOST}"
: "${SSH_USER:?defina SSH_USER}"
SSH_PORT="${SSH_PORT:-22}"
APP_DIR="${APP_DIR:-/opt/btv/danzeroum}"
SSH_KEY="${SSH_KEY:-${HOME}/.ssh/danzeroum_deploy}"

echo "==> Deploy em ${SSH_USER}@${SSH_HOST}:${APP_DIR} (porta ${SSH_PORT})"

ssh -p "${SSH_PORT}" -i "${SSH_KEY}" -o StrictHostKeyChecking=accept-new \
  "${SSH_USER}@${SSH_HOST}" \
  "set -e; cd '${APP_DIR}' && git pull --ff-only && docker compose up -d --remove-orphans && docker compose ps"

echo "✅ Deploy concluído."
