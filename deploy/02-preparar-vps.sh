#!/usr/bin/env bash
# ============================================================
# 02 — Prepara o VPS (rode NO VPS, via SSH, como o usuário de deploy ou com sudo).
# Cria a estrutura de pastas, ajusta permissões, instala o autorized_keys e
# deixa o arquivo de config SMTP pronto para você preencher.
#
# Uso:
#   DOMAIN=danzeroum.com \
#   DEPLOY_USER=$(whoami) \
#   PUBKEY="ssh-ed25519 AAAA... deploy-danzeroum" \
#   bash 02-preparar-vps.sh
# ============================================================
set -euo pipefail

# ---- Parâmetros (ajuste conforme seu VPS) ----
DOMAIN="${DOMAIN:-danzeroum.com}"
BASE_DIR="${BASE_DIR:-/var/www/${DOMAIN}}"     # pasta base do site
WEBROOT="${WEBROOT:-${BASE_DIR}/public_html}"  # web root (= DEPLOY_PATH no GitHub)
CONFIG_FILE="${BASE_DIR}/danzeroum-smtp-config.php"  # config SMTP FORA do web root
DEPLOY_USER="${DEPLOY_USER:-$(whoami)}"
PUBKEY="${PUBKEY:-}"

echo "==> Domínio:    ${DOMAIN}"
echo "==> Web root:   ${WEBROOT}   (use isto no secret DEPLOY_PATH)"
echo "==> Config SMTP:${CONFIG_FILE}"
echo "==> Usuário:    ${DEPLOY_USER}"
echo

# ---- 1) Estrutura de pastas ----
sudo mkdir -p "${WEBROOT}"
sudo chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${BASE_DIR}"
find "${WEBROOT}" -type d -exec chmod 755 {} \; 2>/dev/null || true
echo "✅ Pastas criadas."

# ---- 2) authorized_keys (chave pública de deploy) ----
if [[ -n "${PUBKEY}" ]]; then
  mkdir -p "${HOME}/.ssh"
  touch "${HOME}/.ssh/authorized_keys"
  chmod 700 "${HOME}/.ssh"; chmod 600 "${HOME}/.ssh/authorized_keys"
  if ! grep -qF "${PUBKEY}" "${HOME}/.ssh/authorized_keys"; then
    echo "${PUBKEY}" >> "${HOME}/.ssh/authorized_keys"
    echo "✅ Chave pública adicionada ao authorized_keys."
  else
    echo "ℹ️  Chave pública já estava no authorized_keys."
  fi
else
  echo "⚠️  PUBKEY não informada — adicione manualmente sua chave pública em ~/.ssh/authorized_keys."
fi

# ---- 3) Config SMTP (fora do web root) ----
if [[ ! -f "${CONFIG_FILE}" ]]; then
  cat > "${CONFIG_FILE}" <<'PHP'
<?php
// Credenciais SMTP do formulário (contato.php). NÃO deixe no web root.
return [
    'host'       => 'smtp.hostinger.com',
    'port'       => 465,
    'encryption' => 'ssl',                 // 'ssl' (465) ou 'tls' (587)
    'username'   => 'contato@danzeroum.com',
    'password'   => 'COLOQUE_A_SENHA_AQUI',
    'from'       => 'contato@danzeroum.com',
    'from_name'  => 'Site Danzeroum',
];
PHP
  chmod 640 "${CONFIG_FILE}"
  echo "✅ Modelo de config SMTP criado em ${CONFIG_FILE} — EDITE e coloque a senha real."
else
  echo "ℹ️  Config SMTP já existe em ${CONFIG_FILE} (não sobrescrevi)."
fi

# ---- 4) Checagens úteis ----
echo
echo "==> PHP: $(command -v php >/dev/null && php -v | head -1 || echo 'NÃO encontrado — instale PHP/php-fpm')"
echo "==> rsync: $(command -v rsync >/dev/null && echo ok || echo 'NÃO encontrado — sudo apt install rsync')"
echo
echo "Pronto. Configure os secrets no GitHub:"
echo "  SSH_HOST=<ip/host>  SSH_USER=${DEPLOY_USER}  SSH_PORT=22"
echo "  DEPLOY_PATH=${WEBROOT}  SSH_PRIVATE_KEY=<conteúdo da chave privada>"
