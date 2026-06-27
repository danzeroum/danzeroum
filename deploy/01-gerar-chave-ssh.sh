#!/usr/bin/env bash
# ============================================================
# 01 — Gera o par de chaves SSH dedicado ao deploy (rode LOCALMENTE).
# A chave PÚBLICA vai para o VPS; a PRIVADA vira o secret SSH_PRIVATE_KEY no GitHub.
# ============================================================
set -euo pipefail

KEY_DIR="${HOME}/.ssh"
KEY_FILE="${KEY_DIR}/danzeroum_deploy"

mkdir -p "${KEY_DIR}"

if [[ -f "${KEY_FILE}" ]]; then
  echo "⚠️  Já existe ${KEY_FILE}. Reutilizando a chave existente."
else
  ssh-keygen -t ed25519 -C "deploy-danzeroum" -f "${KEY_FILE}" -N ""
  echo "✅ Chave gerada em ${KEY_FILE}"
fi

echo
echo "==================================================================="
echo " 1) CHAVE PÚBLICA — adicione no VPS em ~/.ssh/authorized_keys"
echo "    (o script 02-preparar-vps.sh faz isso pra você)"
echo "==================================================================="
cat "${KEY_FILE}.pub"
echo
echo "==================================================================="
echo " 2) CHAVE PRIVADA — copie TUDO abaixo para o secret SSH_PRIVATE_KEY"
echo "    no GitHub: Settings → Secrets and variables → Actions → New secret"
echo "==================================================================="
cat "${KEY_FILE}"
echo
echo "==================================================================="
echo " Para adicionar a pública direto no VPS (se tiver acesso por senha):"
echo "   ssh-copy-id -i ${KEY_FILE}.pub <USUARIO>@<HOST_DO_VPS>"
echo "==================================================================="
