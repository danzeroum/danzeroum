#!/usr/bin/env bash
# ============================================================
# 04 — Configura os secrets do deploy no GitHub via gh CLI.
# Rode LOCALMENTE, com o gh autenticado (gh auth login).
#
# Uso:
#   SSH_HOST=203.0.113.10 \
#   SSH_USER=root \
#   SSH_PORT=22 \
#   APP_DIR=/opt/btv/danzeroum \
#   SSH_KEY=~/.ssh/danzeroum_deploy \
#   bash deploy/04-configurar-secrets.sh
# ============================================================
set -euo pipefail

REPO="${REPO:-danzeroum/danzeroum}"
: "${SSH_HOST:?defina SSH_HOST}"
: "${SSH_USER:?defina SSH_USER}"
APP_DIR="${APP_DIR:-/opt/btv/danzeroum}"
SSH_PORT="${SSH_PORT:-22}"
SSH_KEY="${SSH_KEY:-${HOME}/.ssh/danzeroum_deploy}"

command -v gh >/dev/null || { echo "❌ instale o GitHub CLI: https://cli.github.com"; exit 1; }
[[ -f "${SSH_KEY}" ]] || { echo "❌ chave privada não encontrada em ${SSH_KEY} (rode 01-gerar-chave-ssh.sh)"; exit 1; }

echo "==> Configurando secrets em ${REPO}"
gh secret set SSH_HOST        -R "${REPO}" -b "${SSH_HOST}"
gh secret set SSH_USER        -R "${REPO}" -b "${SSH_USER}"
gh secret set SSH_PORT        -R "${REPO}" -b "${SSH_PORT}"
gh secret set APP_DIR         -R "${REPO}" -b "${APP_DIR}"
gh secret set SSH_PRIVATE_KEY -R "${REPO}" < "${SSH_KEY}"

echo "✅ Secrets configurados:"
gh secret list -R "${REPO}"
