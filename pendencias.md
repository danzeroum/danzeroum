# Pendências — implementação do plano (Buscador de Oportunidades Públicas)

Documento para você revisar. Lista o que **foi entregue**, o que **ficou pendente** e as
**decisões** que dependem de você (segredos, infraestrutura, provedor, acesso a sites).

Data: 2026-06-30.

---

## ✅ Entregue (PRs já mergeados em `main`)

| PR | Frente | Resumo |
|----|--------|--------|
| #34 | 1 | Scorer LLM via **DeepSeek** na porta `LLMProvider` + extração de PDF do edital + `POST /score`. Fallback heurístico sem chave. |
| #35 | 2 | **Analytics de negócio** no painel: `GET /analytics` (win rate, valor ganho/perdido, pipeline, série mensal) + gráficos no Dashboard. |
| #36 | 3 | **Alerta ativo de vencimento de certidões**: varredura (30/15/7 dias), e-mail, `GET /documents/expiring`, integração ao `/alerts` e ao loop `schedule`. |
| #38 | 4 | **Unificação dos CRMs**: `scripts/crm_sync.py` sincroniza leads do flat-file → tabela `clients` (idempotente). |
| #39 | 5 | **Geração de PDF** da proposta (`GET /proposals/{id}/pdf`) + `submitted_at` no envio (alimenta analytics). |
| #37 | 7 | **Calculadora corrigida**: faixas progressivas reais do Simples (Anexo III/IV com parcela a deduzir) + ISS opcional + alíquota efetiva. |
| #40 | 8 (parcial) | **Notificação multicanal**: `TelegramNotifier` + `MultiNotifier` (e-mail + Telegram). |

---

## ⛔ Pendente — exige decisão/acesso seu

### Frente 6 — Ativar fontes Compras SP (BEC) e Prefeitura SP  *(bloqueada)*
Os adaptadores existem (`tracker/danzeroum_tracker/adapters/scraper.py`), mas os seletores
CSS estão marcados como "a confirmar" — placeholders nunca validados contra o HTML real.
**Não dá para calibrar sem acesso às páginas reais** (e o scraping de portais públicos é
frágil/muda com frequência).
- **Decisão necessária:** (a) confirmar se os portais ainda usam as URLs em `config.py`
  (`bec.sp.gov.br`, `e-negocioscidadesp.prefeitura.sp.gov.br`); (b) me autorizar a acessar as
  páginas ao vivo para inspecionar o HTML e ajustar os seletores, **ou** me enviar um HTML de
  exemplo de cada listagem; (c) avaliar se há **API oficial** (preferível a scraping).
- Enquanto isso, o default segue `TRACKER_SOURCES=pncp` (1 fonte).

### Frente 8 — resto da robustez operacional
- **Redis + Celery** (fila/retry no lugar do loop `sleep`): exige novos serviços no
  `docker-compose` e refator do agendamento. **Decisão:** vale a complexidade agora, ou o
  loop diário atual basta? (volume de coleta é baixo — poucos acessos/dia.)
- **Object storage (MinIO/S3)**: hoje os arquivos vão como bytes no Postgres
  (`api/migrations/002_add_file_data.sql`). Migrar exige bucket + credenciais + migração dos
  dados. **Decisão:** MinIO (self-hosted) ou S3? Credenciais.
- **WhatsApp Business API**: a empresa usa o WhatsApp `5511996685998`, mas a API oficial
  exige provedor (Meta Cloud API **ou** Twilio), número aprovado e token. **Decisão:** qual
  provedor? (O Telegram já entregue cobre o "multicanal" no curto prazo.)

---

## ⚠️ Decisões técnicas transversais (recomendações)

1. **CI para `api/` e `web/`** — hoje **não há** CI para esses diretórios (só `tracker/` e
   `docker/`). As PRs de API/web foram validadas **localmente** (pytest + `tsc`/build), mas
   sem porteiro automático. **Recomendo** adicionar dois workflows: `api_ci` (pytest em
   `api/tests`) e `web_ci` (`tsc -b && vite build` + `oxlint`). Posso fazer isso numa PR.

2. **Runner de migrations da API** — `api/migrations/*.sql` não têm runner automático (só o
   `tracker/sql/schema.sql` é aplicado no Docker/CI). Isso **bloqueou** três itens menores:
   - **Histórico de cálculos** (Frente 7, previsto na V2).
   - **Vínculo persistido proposta↔cálculo de preço** (Frente 5).
   - **`clients.external_id`** para dedupe do CRM à prova de homônimos (Frente 4 — hoje o
     dedupe usa e-mail/nome).
   **Decisão:** definir o mecanismo (ex.: aplicar `api/migrations/*.sql` no entrypoint do
   container, ou adotar Alembic). Com isso definido, eu entrego os três itens.

3. **DeepSeek (Frente 1)** — implementado e testado com provider mockado. **Ao configurar a
   `DEEPSEEK_API_KEY` real**, validar contra a API ao vivo (nomes `deepseek-v4-flash`/`-pro`
   confirmados na doc, mas convém checar com a chave). Não implementei a **escalada para
   `deepseek-v4-pro`** nos casos `REVIEW` (fica como melhoria — custo extra só nos difíceis).

4. **Download do anexo do edital (Frente 1)** — o módulo de extração (`extraction.py`) está
   pronto e o `LLMScorer` lê texto de `raw_json`, mas **os adaptadores ainda não baixam os
   anexos**. Para o LLM ver o edital completo, falta o PNCP popular a URL do anexo em
   `raw_json` e chamar `download_and_extract`. **Decisão/efeito:** quero ligar isso (custa
   requests extras por edital na coleta)?

5. **Cron dedicado do alerta de certidões (Frente 3)** — já roda no loop `schedule` (diário).
   Se preferir um **GitHub Action** diário, é preciso `DATABASE_URL` + segredos SMTP nos
   secrets do repo (hoje não há). **Decisão:** manter no loop ou criar a Action?

6. **Cuidado de dados (LLM)** — confirmado no código: **só o edital (público)** vai ao
   DeepSeek; documentos internos (certidões, contrato social, atestados) **nunca** entram no
   prompt. Mantido como regra.

---

## 🌿 Nota sobre branches/PRs
As entregas foram feitas como **PRs estratégicas por frente** (`claude/frente-N-*`), cada uma
mergeada em `main` após o CI. A branch designada `claude/procurement-tracker-analysis-ubov2k`
**não recebeu código** (ficou igual à `main`). Se preferir que o trabalho futuro vá para ela,
me avise.
