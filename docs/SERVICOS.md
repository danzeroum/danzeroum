# Serviços Danzeroum — padrão uniforme

Visão única de **todos os serviços** do repositório: como cada um é definido, roda e
faz deploy, com convenções consistentes (Docker Compose, `restart`, healthcheck,
project name) e uma esteira de CI/CD comum.

## Serviços

| Serviço | Stack | Compose | Imagem/Build | CI |
|---|---|---|---|---|
| **Site comercial** | nginx + php-fpm | `docker-compose.yml` (raiz) | `nginx:1.27-alpine`, `php:8.3-fpm-alpine` | `services_ci.yml` (valida compose) |
| **Rastreador de licitações** | Postgres + coletor | `tracker/docker-compose.yml` | build local + `postgres:16-alpine` | `tracker_ci.yml` (ruff + pytest), `services_ci.yml` |

> O **CRM** (`scripts/crm_collector.py` + `crm/*.json`) não é um serviço em runtime —
> roda como job agendado no GitHub Actions (`crm_collect.yml`), não no VPS.

## Convenções uniformes (todos os compose)

- `name:` define o project name (`danzeroum-site`, `danzeroum-tracker`) — stacks isolados.
- `restart: unless-stopped` em todo serviço de longa duração.
- `healthcheck` onde aplicável (nginx no site; Postgres no tracker).
- Sem segredos no compose: variáveis com default (`${VAR:-default}`) ou `env_file: .env`.

## Rodar localmente

```bash
# Site
cp .env.example .env            # SMTP_* (opcional p/ formulário de contato)
docker compose up -d

# Rastreador
cd tracker && cp .env.example .env && docker compose up -d --build
```

## Deploy (VPS, automático)

`/.github/workflows/deploy.yml` roda a cada push na `main` e sobe **todos os serviços**
no VPS, de forma idempotente:

```
git pull --ff-only
docker compose up -d --remove-orphans                              # site
docker compose -f tracker/docker-compose.yml up -d --build ...     # tracker
```

### Secrets necessários (Settings → Secrets and variables → Actions)

| Secret | Descrição |
|---|---|
| `SSH_PRIVATE_KEY` | Chave privada SSH com acesso ao VPS |
| `SSH_HOST` | Host/IP do VPS |
| `SSH_USER` | Usuário SSH |
| `SSH_PORT` | Porta SSH (default 22) |
| `APP_DIR` | Diretório do projeto no VPS (default `/opt/btv/danzeroum`) |

> **Enquanto `SSH_PRIVATE_KEY`/`SSH_HOST` não estiverem configurados, o deploy é
> _pulado com aviso_ (não falha).** Assim os merges na `main` não ficam vermelhos por
> falta de credencial. Ao configurar os secrets, o deploy passa a executar automaticamente.

## CI/CD — esteira comum

| Workflow | Dispara em | O que faz |
|---|---|---|
| `tracker_ci.yml` | mudanças em `tracker/**` | ruff + pytest (Postgres real) |
| `services_ci.yml` | mudanças em qualquer compose / `docker/**` | `docker compose config` nos dois stacks |
| `deploy.yml` | push na `main` (exceto docs/crm/scripts) | deploy de todos os serviços no VPS (gated por secret) |
| `crm_collect.yml` | agendado (semanal) | regenera dados não-pessoais do CRM |
