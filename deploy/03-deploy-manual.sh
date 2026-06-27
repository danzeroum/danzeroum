#!/usr/bin/env bash
# ============================================================
# 03 — Deploy MANUAL do site para o VPS (rode LOCALMENTE, na raiz do repo).
# Faz o mesmo que o GitHub Actions: rsync dos arquivos para o web root.
# Útil para o primeiro deploy ou quando quiser publicar sem passar pelo git.
#
# Uso:
#   SSH_HOST=203.0.113.10 \
#   SSH_USER=deploy \
#   SSH_PORT=22 \
#   DEPLOY_PATH=/var/www/danzeroum.com/public_html \
#   SSH_KEY=~/.ssh/danzeroum_deploy \
#   bash deploy/03-deploy-manual.sh
# ============================================================
set -euo pipefail

: "${SSH_HOST:?defina SSH_HOST}"
: "${SSH_USER:?defina SSH_USER}"
: "${DEPLOY_PATH:?defina DEPLOY_PATH}"
SSH_PORT="${SSH_PORT:-22}"
SSH_KEY="${SSH_KEY:-${HOME}/.ssh/danzeroum_deploy}"

# Vai para a raiz do repositório (este script está em deploy/)
cd "$(dirname "$0")/.."

echo "==> Publicando em ${SSH_USER}@${SSH_HOST}:${DEPLOY_PATH} (porta ${SSH_PORT})"
echo "==> Chave: ${SSH_KEY}"
read -r -p "Confirma o deploy com --delete (servidor fica idêntico ao repo)? [s/N] " ok
[[ "${ok}" =~ ^[sS]$ ]] || { echo "Cancelado."; exit 1; }

rsync -avz --delete \
  --exclude='.git' \
  --exclude='.github' \
  --exclude='.gitignore' \
  --exclude='README.md' \
  --exclude='deploy' \
  --exclude='smtp-config.example.php' \
  -e "ssh -p ${SSH_PORT} -i ${SSH_KEY} -o StrictHostKeyChecking=accept-new" \
  ./ "${SSH_USER}@${SSH_HOST}:${DEPLOY_PATH}/"

echo "✅ Deploy concluído."
