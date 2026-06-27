# Danzeroum — site comercial + portfólio

Site institucional da **Danzeroum**, estúdio de engenharia de IA e software sob medida
para médias empresas. Mistura uma **landing comercial** (serviços, processo, diferenciais,
modelos de engajamento, FAQ, conversão) com um **portfólio** de cases reais validados a
partir dos repositórios públicos em [github.com/danzeroum](https://github.com/danzeroum).

> Produção: **https://danzeroum.com** — roda como serviço Docker em `/opt/btv/danzeroum`,
> atrás do ingress nginx do ambiente BuildToValue.

## Stack

Frontend **HTML/CSS/JS estático** (design system "golden hour", tema claro/escuro, mobile-first)
+ um pequeno **handler PHP** para o formulário de contato (PHPMailer/SMTP). Empacotado como
**2 containers Docker**:

- `danzeroum-frontend` — `nginx:1.27-alpine`, serve `public/` e faz proxy do `/contato.php` para o PHP.
- `danzeroum-php` — `php:8.3-fpm-alpine`, executa `public/contato.php` (envia o e-mail via SMTP).

O **ingress** (`/opt/btv/ingress`) faz `proxy_pass http://danzeroum-frontend:80`, como os demais
serviços do ambiente.

## Estrutura

```
.
├── public/                  # web root (montado nos containers)
│   ├── index.html           # landing comercial + cases
│   ├── contato.php          # handler do formulário (SMTP via PHPMailer, lê do ambiente)
│   ├── privacidade.html · obrigado.html · 404.html
│   ├── robots.txt · sitemap.xml
│   ├── assets/              # styles.css, theme.js, projects.js, og-image.png, favicon.svg
│   └── lib/PHPMailer/       # PHPMailer 6.9.3 versionado (sem Composer)
├── docker/nginx.conf        # nginx do container (estático + fastcgi p/ contato.php)
├── docker-compose.yml       # serviços danzeroum-frontend + danzeroum-php
├── .env.example             # SMTP_* + MAIL_TO (copie para .env e preencha)
├── deploy/                  # scripts de configuração e deploy
└── .github/workflows/deploy.yml  # git pull + docker compose up no push p/ main
```

## Subir no VPS (uma vez)

```bash
# 1. Clonar o projeto em /opt/btv
sudo git clone https://github.com/danzeroum/danzeroum.git /opt/btv/danzeroum
cd /opt/btv/danzeroum

# 2. Configurar o SMTP do formulário
cp .env.example .env
nano .env          # preencha SMTP_PASS (e ajuste host/porta se preciso)

# 3. Subir os containers
docker compose up -d
docker compose ps
```

> O script `deploy/02-preparar-vps.sh` automatiza os passos acima.
> A rede externa `btv-prod-net` precisa existir (`docker network ls`). Se o nome for outro,
> ajuste em `docker-compose.yml`.

### Apontar o ingress para o container

No `/opt/btv/ingress/nginx/nginx.conf`, no `server { … server_name danzeroum.com; }`,
troque o bloco estático pelo proxy (mantendo os redirects 80→443 e www→apex):

```nginx
# antes:  root /usr/share/nginx/portfolio; index index.html;
#         location / { try_files $uri $uri/ =404; }
# depois:
location ~* (wp-login|login\.cgi|\.git|env) { return 444; }
location / { set $upstream "http://danzeroum-frontend:80"; proxy_pass $upstream; }
```

Recarregue o ingress: `docker exec <ingress> nginx -t && docker exec <ingress> nginx -s reload`.

## Formulário de contato

- **WhatsApp:** `5511996685998` (links `https://wa.me/5511996685998`).
- **Formulário:** `public/contato.php` envia para `MAIL_TO` via **SMTP autenticado (PHPMailer)**,
  com honeypot anti-spam, e redireciona para `/obrigado.html` (erro → `?erro=1`).
  As credenciais vêm do **`.env`** (variáveis `SMTP_*`, `MAIL_TO`) — nunca vão para o git.
  Hostinger: `SMTP_HOST=smtp.hostinger.com`, `465`/`ssl` ou `587`/`tls`.
  Sem `SMTP_HOST` definido, cai no fallback `mail()`.

## Deploy contínuo (GitHub Actions)

`.github/workflows/deploy.yml` — a cada push no `main` (ou *Run workflow*), conecta no VPS por SSH e
roda `git pull --ff-only && docker compose up -d`.

### Secrets (Settings → Secrets and variables → Actions)

| Secret | O que é | Exemplo |
|--------|---------|---------|
| `SSH_HOST` | IP/host do VPS | `203.0.113.10` |
| `SSH_USER` | usuário SSH | `root` |
| `SSH_PORT` | porta SSH (opcional, default `22`) | `22` |
| `SSH_PRIVATE_KEY` | chave privada cuja pública está no `authorized_keys` do VPS | conteúdo da chave |
| `APP_DIR` | diretório do projeto no VPS (opcional, default `/opt/btv/danzeroum`) | `/opt/btv/danzeroum` |

Scripts auxiliares em `deploy/`: `01` gera a chave SSH, `02` prepara o VPS, `03` faz deploy manual,
`04` configura os secrets via `gh`, e `healthcheck.sh` confere o site no ar. O DNS **não muda**.

## Desenvolvimento local

```bash
docker compose up -d            # site em http://localhost  (via ingress, ajuste a porta se quiser)
# ou, sem docker, só o estático:
cd public && python3 -m http.server 8000
# com o formulário PHP:
cd public && php -S localhost:8000
```

### Sobre os cases
Os 23 cases em `public/assets/projects.js` correspondem **exatamente** aos repositórios
**públicos** de `github.com/danzeroum`. Para destacar um projeto privado, **torne-o público
primeiro** e adicione o objeto ao array `PROJECTS` com `featured: true`.
