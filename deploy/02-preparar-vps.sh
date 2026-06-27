#!/usr/bin/env bash
# ============================================================
# 02 — Prepara o VPS (rode NO VPS, via SSH). Clona o projeto em /opt/btv,
# cria o .env e sobe os containers Docker.
#
# Uso:
#   APP_DIR=/opt/btv/danzeroum \
#   PUBKEY="ssh-ed25519 AAAA... deploy-danzeroum" \
#   bash 02-preparar-vps.sh
# ============================================================
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/btv/danzeroum}"
REPO_URL="${REPO_URL:-https://github.com/danzeroum/danzeroum.git}"
PUBKEY="${PUBKEY:-}"

echo "==> Projeto:  ${APP_DIR}"
echo "==> Repo:     ${REPO_URL}"
echo

# ---- 1) Clona (ou atualiza) o projeto ----
if [[ -d "${APP_DIR}/.git" ]]; then
  echo "ℹ️  Repo já existe — atualizando."
  git -C "${APP_DIR}" pull --ff-only
else
  sudo mkdir -p "$(dirname "${APP_DIR}")"
  sudo git clone "${REPO_URL}" "${APP_DIR}"
  sudo chown -R "$(whoami):$(whoami)" "${APP_DIR}" 2>/dev/null || true
fi
echo "✅ Projeto em ${APP_DIR}"

# ---- 2) authorized_keys (chave pública de deploy p/ o GitHub Actions) ----
if [[ -n "${PUBKEY}" ]]; then
  mkdir -p "${HOME}/.ssh"; touch "${HOME}/.ssh/authorized_keys"
  chmod 700 "${HOME}/.ssh"; chmod 600 "${HOME}/.ssh/authorized_keys"
  if ! grep -qF "${PUBKEY}" "${HOME}/.ssh/authorized_keys"; then
    echo "${PUBKEY}" >> "${HOME}/.ssh/authorized_keys"
    echo "✅ Chave pública de deploy adicionada."
  else
    echo "ℹ️  Chave pública já estava no authorized_keys."
  fi
else
  echo "⚠️  PUBKEY não informada — adicione manualmente em ~/.ssh/authorized_keys (chave do passo 01)."
fi

# ---- 3) .env (credenciais SMTP) ----
if [[ ! -f "${APP_DIR}/.env" ]]; then
  cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
  chmod 600 "${APP_DIR}/.env"
  echo "✅ .env criado em ${APP_DIR}/.env — EDITE e coloque a senha real (SMTP_PASS)."
else
  echo "ℹ️  .env já existe (não sobrescrevi)."
fi

# ---- 4) Sobe os containers ----
echo
echo "==> Docker: $(command -v docker >/dev/null && docker --version || echo 'NÃO encontrado')"
echo "Edite o .env e depois rode:"
echo "  cd ${APP_DIR} && docker compose up -d && docker compose ps"
echo
echo "Depois ajuste o ingress (/opt/btv/ingress/nginx/nginx.conf) para:"
echo '  location / { set $upstream "http://danzeroum-frontend:80"; proxy_pass $upstream; }'
echo "e recarregue:  docker exec <ingress> nginx -t && docker exec <ingress> nginx -s reload"
echo
echo "Secrets do GitHub (Actions):"
echo "  SSH_HOST=<ip>  SSH_USER=$(whoami)  SSH_PORT=22  APP_DIR=${APP_DIR}  SSH_PRIVATE_KEY=<chave privada>"
