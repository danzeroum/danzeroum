# Rastreador de Oportunidades — Danzeroum (V1)

Subprojeto **isolado** (não toca no site em `../`): coleta editais de TI de órgãos
públicos, normaliza, pontua a aderência ao perfil da Danzeroum e persiste em
PostgreSQL. Roda via Docker com poucos acessos por dia (uma coleta diária por padrão),
single-tenant (só Danzeroum). Desenho para crescer — ver `../docs/buscador-oportunidades/BLUEPRINT.md`.

## O que a V1 entrega

- **Adaptadores**: PNCP e Compras.gov.br (via API) + Compras SP e Prefeitura SP
  (via **scraping** HTML, com seletores CSS marcados como "a confirmar"). Helpers de
  parsing compartilhados em `adapters/common.py`; scraping genérico em `adapters/scraper.py`.
  Fontes ativas controladas por `TRACKER_SOURCES` (default `pncp`).
- **Scorer heurístico** (sem LLM, sem custo, sem chave de API) — interface agnóstica,
  pronta para plugar OpenAI/Gemini/Claude/Ollama numa rodada futura.
- **PostgreSQL** com dedupe por `(source, external_id)` e schema versionado (`sql/schema.sql`).
- **CLI** (`schema`, `search`, `collect`, `list`, `report`, `schedule`) e loop de agendamento.
- **Relatório** (`report`) e **alertas por e-mail** (opt-in via SMTP; no-op se não configurado).

> Arquitetura hexagonal: o core só conhece as interfaces (`OrgaoAdapter`, `Scorer`,
> `TenderRepository`). Novos órgãos ou um provedor de LLM entram sem mexer no núcleo.

## Rodar via Docker (recomendado)

```bash
cd tracker
cp .env.example .env          # ajuste se quiser; nenhum segredo é obrigatório
docker compose up -d --build  # sobe Postgres + coletor (loop diário)
docker compose logs -f tracker
```

O schema é aplicado automaticamente na criação do banco. O serviço `tracker` roda
`collect` a cada `COLLECT_INTERVAL_HOURS` (default 24h).

## Rodar a CLI manualmente

```bash
pip install -e ".[dev]"

python -m danzeroum_tracker schema            # imprime o JSON Schema do scorer
python -m danzeroum_tracker search --limit 10 # busca + pontua (não persiste)
DATABASE_URL=postgresql://danzeroum:danzeroum@localhost:5432/oportunidades \
  python -m danzeroum_tracker collect         # coleta + dedupe + score + persiste

python -m danzeroum_tracker report --format md   # relatório (text|md|json)
```

## Alertas por e-mail (opcional)

Se `SMTP_HOST` e `MAIL_TO` estiverem definidos (mesmas variáveis do site), o `collect`/
`schedule` envia um e-mail com as oportunidades de alta aderência (`fit ≥ TRACKER_MIN_FIT`
e recomendação ≠ `SKIP`). **Sem SMTP configurado, é no-op** — nada é enviado.

## Configuração (variáveis de ambiente)

| Variável | Default | Descrição |
|---|---|---|
| `DATABASE_URL` | *(vazio → memória)* | Conexão PostgreSQL. Vazio usa repositório em memória. |
| `PNCP_BASE_URL` | `https://pncp.gov.br/api/consulta/v1` | Base da API do PNCP. |
| `COMPRAS_GOV_BASE_URL` | `https://dadosabertos.compras.gov.br` | Base da API do Compras.gov.br. |
| `COMPRAS_SP_BASE_URL` | `https://www.bec.sp.gov.br` | Base do portal Compras SP (scraping). |
| `PREF_SP_BASE_URL` | `https://e-negocioscidadesp.prefeitura.sp.gov.br` | Base do portal Prefeitura SP (scraping). |
| `TRACKER_SOURCES` | `pncp` | Fontes (CSV): `pncp`, `comprasgov`, `comprassp`, `prefsp`. |
| `TRACKER_UF` | `SP` | UF de busca. |
| `TRACKER_KEYWORDS` | *(perfil de TI)* | CSV de palavras-chave; vazio usa o default embutido. |
| `TRACKER_SCORER` | `heuristic` | Scorer ativo. |
| `COLLECT_INTERVAL_HOURS` | `24` | Frequência do loop `schedule`. |
| `TRACKER_MIN_FIT` | `0.4` | Aderência mínima para gerar alerta. |
| `SMTP_HOST` / `MAIL_TO` | *(vazio)* | Defina ambos para ativar alertas por e-mail (senão no-op). |
| `SMTP_PORT` / `SMTP_ENCRYPTION` | `465` / `ssl` | Porta e criptografia (`ssl`/`tls`). |
| `SMTP_USER` / `SMTP_PASS` / `SMTP_FROM` | *(vazio)* | Credenciais e remetente. |

## Testes

```bash
pip install -e ".[dev]"
ruff check .
pytest -q                       # unitários (a integração Postgres é pulada sem DATABASE_URL)

# Com Postgres real (roda também os testes de integração):
DATABASE_URL=postgresql://danzeroum:danzeroum@localhost:5432/oportunidades pytest -q
```

A CI (`.github/workflows/tracker_ci.yml`) sobe um Postgres, aplica o schema, roda
`ruff` e `pytest` (incluindo integração). Não faz deploy.

## Próximos passos (rodada futura)

- Adaptadores Compras.gov / Compras SP / Prefeitura SP.
- Provedor de LLM concreto (decisão de provedor + custo) atrás de `Scorer`/`LLMProvider`.
- Alertas por e-mail (reusar PHPMailer do site) e dashboard.

> ⚠️ Os campos/endpoints exatos da API do PNCP devem ser confirmados na primeira
> execução real — o parsing é resiliente a variações de nomes, mas o contrato pode
> mudar entre versões da API.
