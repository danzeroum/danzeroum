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

### Frente 6 — Ativar fontes Compras SP (BEC) e Prefeitura SP  *(investigada ao vivo — inviável agora)*
Com a internet liberada, investiguei os dois portais ao vivo (2026-06-30):
- **Prefeitura SP** (`e-negocioscidadesp.prefeitura.sp.gov.br`): **inacessível** deste ambiente
  — o handshake TLS falha (HTTP 000) em `www` e sem `www`. Bloqueio de rede/host, não de código.
- **BEC SP** (`bec.sp.gov.br`): o caminho antigo em `config.py` (`OfertaPesquisa.aspx`) **está
  morto (404)**. O portal é ASP.NET WebForms: a listagem de **ofertas abertas** (com objeto,
  valor e prazo) só aparece via fluxo de **postback/viewstate** (busca → submit → paginação),
  frágil e de alta manutenção. As páginas GET-áveis que encontrei (`pregaoOCSuspensa.aspx` = log
  de OCs suspensas; `DetalheOCItens.aspx` = catálogo de itens) **não** trazem objeto/valor/prazo
  de oportunidades, então não servem ao modelo `Tender`.
- **Conclusão/recomendação:** o ganho marginal é baixo — pela **Lei 14.133/2021**, os entes
  públicos são obrigados a publicar no **PNCP** (já integrado e funcionando), que hoje agrega a
  maior parte das licitações municipais/estaduais de SP. Sugiro **não** investir no scraping do
  BEC/Prefeitura por ora e manter o foco no PNCP. Se houver uma **API oficial** do BEC/Prefeitura
  no futuro, plugo um adaptador. Default segue `TRACKER_SOURCES=pncp`.
- **Em vez disso**, usei o acesso liberado para entregar a pendência de maior valor (abaixo).

### ✅ Resolvido com o acesso liberado — download do anexo do edital (PNCP) para o LLM
A pendência "o LLM só vê título/descrição" foi **resolvida** (PR desta rodada): validei ao vivo a
API de arquivos do PNCP, o download do **Edital** (vem como **ZIP de PDFs**) e a extração do texto
(ex.: "TERMO DE REFERÊNCIA / OBJETO"). Com `TRACKER_FETCH_EDITAL=true` (e `TRACKER_SCORER=llm`), o
scorer passa a ler o **edital completo**. Best-effort: qualquer falha cai no texto de título/descrição.

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

1. ~~**CI para `api/` e `web/`**~~ — ✅ **RESOLVIDO** (PR desta rodada): novos workflows
   `api_ci.yml` (pytest em `api/tests` + Postgres para o teste de integração do runner) e
   `web_ci.yml` (`npm ci` + `tsc -b && vite build` + `oxlint`).

2. ~~**Runner de migrations da API**~~ — ✅ **RESOLVIDO** (PR desta rodada): `api/migrate.py`
   aplica `api/migrations/*.sql` idempotentemente (controle em `schema_migrations`), rodando no
   startup do contêiner via `api/entrypoint.sh`. Isso **destrava** os três itens abaixo, que
   ficam para uma **próxima rodada** (agora têm onde apoiar):
   - **Histórico de cálculos** (Frente 7, previsto na V2) — nova migration + tabela `calc_history`.
   - **Vínculo persistido proposta↔cálculo de preço** (Frente 5) — coluna/migration.
   - **`clients.external_id`** para dedupe do CRM à prova de homônimos (Frente 4).

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
