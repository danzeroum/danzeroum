#!/usr/bin/env bash
# ============================================================
# Healthcheck pós-deploy — confere se o site respondeu corretamente.
# Uso:  BASE_URL=https://danzeroum.com bash deploy/healthcheck.sh
# ============================================================
set -uo pipefail

BASE_URL="${BASE_URL:-https://danzeroum.com}"
fail=0

check() {
  local path="$1" esperado="$2"
  local code
  code=$(curl -s -o /dev/null -m 15 -w "%{http_code}" "${BASE_URL}${path}")
  if [[ "${code}" == "${esperado}" ]]; then
    echo "✅ ${path} -> ${code}"
  else
    echo "❌ ${path} -> ${code} (esperado ${esperado})"
    fail=1
  fi
}

echo "== Healthcheck em ${BASE_URL} =="
check "/"                    "200"
check "/assets/styles.css"   "200"
check "/assets/og-image.png" "200"
check "/privacidade.html"    "200"
check "/robots.txt"          "200"
check "/sitemap.xml"         "200"
check "/pagina-inexistente"  "404"

# contato.php deve existir e rejeitar GET com redirect (303)
code=$(curl -s -o /dev/null -m 15 -w "%{http_code}" "${BASE_URL}/contato.php")
if [[ "${code}" == "303" || "${code}" == "302" ]]; then
  echo "✅ /contato.php (GET) -> ${code} (redireciona, ok)"
else
  echo "❌ /contato.php (GET) -> ${code} (esperado 303) — PHP pode não estar ativo"
  fail=1
fi

# Código sensível NÃO pode estar acessível pela web (lib do PHPMailer)
code=$(curl -s -o /dev/null -m 15 -w "%{http_code}" "${BASE_URL}/lib/PHPMailer/PHPMailer.php")
if [[ "${code}" == "404" || "${code}" == "403" ]]; then
  echo "✅ /lib/ não exposto (-> ${code})"
else
  echo "⚠️  /lib/PHPMailer/PHPMailer.php -> ${code} — o código da lib não deveria ser servido!"
  fail=1
fi

echo
[[ "${fail}" == "0" ]] && echo "🎉 Tudo verde." || echo "⚠️  Há itens para revisar."
exit "${fail}"
