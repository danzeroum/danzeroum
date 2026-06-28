# RUNBOOK — Rastreador de Oportunidades (tracker)

Guia operacional do `danzeroum-tracker`: subir em produção, ligar alertas por e-mail,
ler a saída da coleta e resolver os problemas mais comuns. Para o **porquê** e o desenho
do sistema, ver [`../docs/buscador-oportunidades/BLUEPRINT.md`](../docs/buscador-oportunidades/BLUEPRINT.md).

> **Escopo.** Este stack é **isolado** do site. O `tracker/docker-compose.yml` sobe um
> PostgreSQL próprio + o coletor em loop. O deploy automático por SSH (`.github/workflows/deploy.yml`)
> sobe **ambos** (site + tracker) quando os secrets estão configurados; sem eles, o tracker
> é subido manualmente no VPS (passos abaixo).

---

## 1. Visão rápida

| Item | Valor |
|---|---|
| Pacote | `danzeroum_tracker` (Python ≥ 3.11) |
| Fontes | `pncp` (default) · `comprasgov` (opt-in, API) · `comprassp` / `prefsp` (scraping, seletores a confirmar) |
| Scoring | `heuristic` (sem LLM, sem chave, sem custo) |
| Persistência | PostgreSQL (schema em `sql/schema.sql`, autoaplicado na 1ª subida) |
| Saídas | comando `report` (text/md/json) + alertas por e-mail (opt-in) |
| Stack | `db` (postgres:16) + `tracker` (loop `schedule`) |

---

## 2. Subir em produção (VPS) — uma vez

No diretório do projeto no VPS (ex.: `/opt/btv/danzeroum`):

```bash
cd tracker
cp .env.example .env
nano .env          # preencha conforme a seção 4
docker compose up -d --build
docker compose ps  # 'db' healthy, 'tracker' up
```

O serviço `tracker` roda `schedule`: executa um `collect` e dorme `COLLECT_INTERVAL_HOURS`
(default 24h) até o próximo. O schema do banco é aplicado automaticamente **na primeira
inicialização** do volume `tracker_pgdata` (ver §7 sobre mudanças de schema depois disso).

---

## 3. Operação do dia a dia

```bash
# Coleta avulsa agora (não espera o ciclo) — mostra o JSON do resultado:
docker compose run --rm tracker collect

# Relatório do acervo (text | md | json):
docker compose run --rm tracker report --format md
docker compose run --rm tracker report --format json --limit 20

# Listar editais persistidos:
docker compose run --rm tracker list --limit 50

# Acompanhar o loop diário:
docker compose logs -f tracker

# Reiniciar / parar o stack:
docker compose restart tracker
docker compose down            # mantém o volume (dados preservados)
```

### Comandos da CLI

| Comando | O que faz | Flags |
|---|---|---|
| `collect` | coleta + dedupe + score + persiste; dispara alertas | — |
| `report` | relatório do acervo (estatísticas + top-N por aderência) | `--format text\|md\|json`, `--limit N` (default 10) |
| `list` | lista editais persistidos (JSON) | `--limit N` (default 50) |
| `search` | busca + pontua **sem persistir** (debug) | `--limit N` (default 20) |
| `schedule` | loop: `collect` a cada `COLLECT_INTERVAL_HOURS` (é o default do contêiner) | — |
| `schema` | imprime o JSON Schema do scorer | — |

---

## 4. Variáveis de ambiente (`.env`)

Tudo tem default sensato; **nenhum segredo é obrigatório** para rodar a V1 (só PNCP, sem e-mail).
Para "produção com e-mail + Compras.gov", o mínimo é a seção SMTP + `TRACKER_SOURCES`.
Variável vazia (`${VAR:-}`) é tratada como "use o default" — não quebra a config.

### Banco (Docker liga `db:5432` sozinho)

| Variável | Default | Nota |
|---|---|---|
| `POSTGRES_USER` | `danzeroum` | |
| `POSTGRES_PASSWORD` | `danzeroum` | **troque em produção** |
| `POSTGRES_DB` | `oportunidades` | |

### Coleta / scoring

| Variável | Default | Nota |
|---|---|---|
| `TRACKER_SOURCES` | `pncp` | CSV: `pncp,comprasgov,comprassp,prefsp` |
| `TRACKER_UF` | `SP` | |
| `TRACKER_KEYWORDS` | (perfil de TI embutido) | CSV; vazio = default |
| `TRACKER_SCORER` | `heuristic` | único disponível hoje |
| `COLLECT_INTERVAL_HOURS` | `24` | frequência do loop |
| `TRACKER_MIN_FIT` | `0.4` | aderência mínima (0–1) para gerar alerta |

### Calibração de endpoint/paginação (avançado — repassados pelo compose)

| Variável | Default | Nota |
|---|---|---|
| `PNCP_BASE_URL` | `https://pncp.gov.br/api/consulta/v1` | base da API do PNCP |
| `COMPRAS_GOV_BASE_URL` | `https://dadosabertos.compras.gov.br` | base do Compras.gov |
| `COMPRAS_SP_BASE_URL` | `https://www.bec.sp.gov.br` | base do BEC (scraping) |
| `PREF_SP_BASE_URL` | `https://e-negocioscidadesp.prefeitura.sp.gov.br` | base e-Negócios (scraping) |
| `TRACKER_PAGE_SIZE` | `50` | itens por página |
| `TRACKER_MAX_PAGES` | `5` | máximo de páginas por fonte |
| `TRACKER_REQUEST_TIMEOUT` | `30` | timeout HTTP (s) |

### E-mail (opt-in — sem `SMTP_HOST` + `MAIL_TO` é no-op, não envia)

| Variável | Default | Exemplo (Hostinger) |
|---|---|---|
| `SMTP_HOST` | (vazio) | `smtp.hostinger.com` |
| `SMTP_PORT` | `465` | `465` (ssl) ou `587` (tls) |
| `SMTP_ENCRYPTION` | `ssl` | `ssl` \| `tls` |
| `SMTP_USER` | (vazio) | `contato@danzeroum.com` |
| `SMTP_PASS` | (vazio) | senha do e-mail |
| `SMTP_FROM` | (vazio → usa `SMTP_USER`) | `contato@danzeroum.com` |
| `SMTP_FROM_NAME` | `Rastreador Danzeroum` | |
| `MAIL_TO` | (vazio) | onde receber os alertas |

> Reutilize exatamente o SMTP que já está no `.env` do **site** (mesmo provedor/credenciais).

---

## 5. Lendo a saída do `collect`

O `collect` imprime um JSON. Campos:

| Campo | Significado |
|---|---|
| `collected` | quantos editais as fontes retornaram nesta rodada |
| `new` | quantos eram inéditos (após dedupe por `source`+`external_id`) |
| `scored` | quantos foram pontuados |
| `alerts` | lista dos que passaram de `TRACKER_MIN_FIT` (título, fit, recomendação, prazo, url) |
| `notified` | quantos e-mails de alerta foram enviados (0 se SMTP no-op ou sem alertas) |

Leitura rápida: `collected > 0` = fontes responderam; `notified > 0` = e-mail saiu
(confira a caixa de `MAIL_TO`, inclusive SPAM).

---

## 6. Checklist de "ligar em produção"

- [ ] `.env` criado em `tracker/` com `POSTGRES_PASSWORD` trocado.
- [ ] SMTP preenchido (`SMTP_HOST` + `MAIL_TO` no mínimo) se quiser alertas.
- [ ] `TRACKER_SOURCES=pncp,comprasgov` se for ligar a 2ª fonte de API.
- [ ] `docker compose up -d --build` → `db` healthy, `tracker` up.
- [ ] `docker compose run --rm tracker collect` → conferir `collected`/`notified`.
- [ ] E-mail de teste recebido (ou `notified: 0` esperado se ainda não há editais aderentes).

---

## 7. Troubleshooting

**`collected: 0` (fontes não retornaram nada).**
O parsing é resiliente, mas o **endpoint/params exato** do PNCP/Compras.gov está marcado
como "a confirmar". Rode `collect`, guarde a saída e, se possível, um exemplo da resposta
crua da API — é o insumo para calibrar o caminho real. Para ajustar a URL base sem mexer
no código, defina `PNCP_BASE_URL` / `COMPRAS_GOV_BASE_URL` (e, se preciso,
`TRACKER_PAGE_SIZE` / `TRACKER_MAX_PAGES`) no `.env` — o compose já repassa essas variáveis.

**E-mail não chegou, mas `notified > 0`.**
Verifique SPAM e as credenciais SMTP. `SMTP_PORT=465`→`SMTP_ENCRYPTION=ssl`;
`587`→`tls`. Confirme que `SMTP_FROM` é um remetente autorizado pelo provedor.

**`notified: 0` mesmo com editais.**
(a) SMTP no-op (`SMTP_HOST` ou `MAIL_TO` vazios); (b) nenhum edital passou de
`TRACKER_MIN_FIT` — baixe o limiar para testar; (c) `alerts` veio vazio porque `new` foi 0
(tudo já estava no banco de rodadas anteriores).

**Erro de conexão ao banco.**
Confirme `db` healthy (`docker compose ps`) e que o `tracker` espera o healthcheck
(`depends_on: condition: service_healthy` já está no compose).

**Mudei o `sql/schema.sql` e nada aconteceu.**
O schema só roda na **1ª inicialização** do volume (via `/docker-entrypoint-initdb.d`).
Para reaplicar em dev: `docker compose down -v` (⚠️ **apaga os dados**) e suba de novo.
Em produção, prefira uma migração manual com `psql` para não perder o acervo.

**Egress bloqueado.**
O VPS precisa alcançar `pncp.gov.br` e `dadosabertos.compras.gov.br`. A rede do site
costuma ser irrestrita; se houver firewall de saída, libere esses hosts.

---

## 8. Backup & restore (acervo)

Os dados ficam no volume `tracker_pgdata`.

```bash
# Backup lógico:
docker compose exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup_oportunidades.sql

# Restore (com o stack no ar):
cat backup_oportunidades.sql | docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

---

## 9. Itens que dependem de decisão/acesso externo

| Pendência | Quem destrava | Como |
|---|---|---|
| Calibrar endpoint PNCP / seletores de scraping | execução real com rede | rodar `collect`, enviar saída + resposta crua da API; ajustar `*_BASE_URL` no `.env` |
| Provedor de LLM concreto | decisão do sócio | escolher provedor; interface `LLMProvider` já pronta |
| Deploy automático (site + tracker) | secrets `SSH_*` | Settings → Secrets and variables → Actions |
