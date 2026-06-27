# Deploy do site Danzeroum no VPS Hostinger

Kit completo para subir o site em produção. O site é estático + `contato.php` (PHP).
O deploy roda automático pelo GitHub Actions a cada push no `main`, e também dá para
publicar manualmente. **O DNS continua apontando para o seu VPS — nada de DNS muda.**

## Scripts deste diretório

| Arquivo | Onde rodar | O que faz |
|---------|------------|-----------|
| `01-gerar-chave-ssh.sh` | seu computador | Gera o par de chaves SSH de deploy e mostra a pública (p/ o VPS) e a privada (p/ o secret) |
| `02-preparar-vps.sh` | no VPS | Cria as pastas, ajusta permissões, instala a chave pública e cria o modelo de config SMTP |
| `03-deploy-manual.sh` | seu computador | Publica o site no VPS via `rsync` (mesma coisa que o Actions faz) |
| `healthcheck.sh` | qualquer lugar | Confere se o site no ar respondeu certo (200/404/redirect e config protegida) |
| `nginx-danzeroum.conf` | no VPS (se usar nginx) | Server block de exemplo (estático + PHP-FPM) |

> Se o seu VPS usa **Apache/LiteSpeed** (comum na Hostinger), o `.htaccess` da raiz do
> repositório já cobre 404, bloqueio de arquivos sensíveis, cache e compressão — é só
> publicar. Use o `nginx-danzeroum.conf` **apenas** se o servidor for nginx.

---

## Passo a passo (uma vez só)

### 1. Gerar a chave de deploy (no seu computador)
```bash
bash deploy/01-gerar-chave-ssh.sh
```
Guarde a **chave pública** e a **chave privada** que ele imprime.

### 2. Preparar o VPS (no VPS, via SSH)
Entre no VPS e rode (ajuste os valores):
```bash
DOMAIN=danzeroum.com \
DEPLOY_USER=$(whoami) \
WEBROOT=/var/www/danzeroum.com/public_html \
PUBKEY="ssh-ed25519 AAAA... deploy-danzeroum" \
bash 02-preparar-vps.sh
```
Depois **edite a senha** real do e-mail:
```bash
nano /var/www/danzeroum.com/danzeroum-smtp-config.php
```

### 3. Configurar os secrets no GitHub
Repositório → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Valor |
|--------|-------|
| `SSH_HOST` | IP ou host do VPS (ex.: `203.0.113.10`) |
| `SSH_USER` | usuário SSH (o `DEPLOY_USER` do passo 2) |
| `SSH_PORT` | `22` (ou a porta do seu VPS) |
| `SSH_PRIVATE_KEY` | conteúdo **inteiro** da chave privada do passo 1 |
| `DEPLOY_PATH` | web root, ex.: `/var/www/danzeroum.com/public_html` |

### 4. Configurar o servidor web (se ainda não houver vhost para o domínio)
- **Apache/LiteSpeed (Hostinger):** aponte o domínio para `…/public_html`. O `.htaccess` já vai junto.
- **nginx:** use `deploy/nginx-danzeroum.conf` (ajuste o socket do PHP-FPM) e recarregue o nginx.
- **HTTPS:** `sudo certbot --nginx -d danzeroum.com -d www.danzeroum.com` (ou `--apache`).

---

## Publicar

### Automático (recomendado)
Qualquer push no `main` dispara o deploy. Para rodar na mão:
**Actions → "Deploy para o VPS Hostinger" → Run workflow**.

### Manual (primeiro deploy ou emergência)
```bash
SSH_HOST=203.0.113.10 SSH_USER=deploy SSH_PORT=22 \
DEPLOY_PATH=/var/www/danzeroum.com/public_html \
SSH_KEY=~/.ssh/danzeroum_deploy \
bash deploy/03-deploy-manual.sh
```

---

## Conferir depois do deploy
```bash
BASE_URL=https://danzeroum.com bash deploy/healthcheck.sh
```
Verifica páginas (200), 404, o redirect do `contato.php` (PHP ativo) e se a config SMTP
**não** está exposta na web.

---

## Avisos importantes
- O `rsync` usa `--delete`: o web root fica **idêntico** ao repositório. Por isso o
  `DEPLOY_PATH` deve ser o web root **exclusivo do site**, e a config SMTP fica **um nível
  acima** (fora do alcance do `--delete`).
- O formulário precisa de **PHP** ativo no VPS. Sem a config SMTP, `contato.php` cai no
  fallback `mail()`.
- Nunca comite `danzeroum-smtp-config.php` (já está no `.gitignore`).
