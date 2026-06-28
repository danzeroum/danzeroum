# Handoff: Buscador de Oportunidades (Danzeroum)

## Overview
Camada operacional de UI para o **rastreador de licitações da Danzeroum** — o sistema que coleta
editais (PNCP, ComprasNet, BEC-SP), pontua cada um com IA/heurística (aderência, risco, complexidade →
**GO / REVIEW / SKIP**) e apoia a decisão de participar, precificar e propor. Hoje o tracker é
**headless** (só CLI + Docker); este pacote especifica e prototipa **11 telas navegáveis** que cobrem
todas as funcionalidades propostas (V1→V3).

O `UI-DESIGN-BRIEF.md` (incluído) explica como o repositório do tracker é a "fonte de verdade" para o
design — qual arquivo responde cada pergunta de UI (schema, scoring, CLI, config). Leia-o primeiro.

## About the Design Files
Os arquivos deste pacote são **referências de design feitas em HTML/React (via Babel in-browser)** —
protótipos que mostram aparência e comportamento pretendidos, **não código de produção para copiar
diretamente**. A tarefa é **recriar estes designs no ambiente do codebase de destino** (o tracker é
Python; o front sugerido é **React + Vite** ou **Next.js**, consumindo uma API a ser criada sobre o
core — ver "Pré-requisito técnico"). Se nenhum front existir ainda, escolha React+Vite e implemente ali,
traduzindo os componentes JSX deste protótipo para componentes reais com data-fetching.

## Fidelity
**Alta fidelidade (hifi).** Cores, tipografia, espaçamentos, estados e interações são finais. Os tokens
estão em `brand/tokens.css` e em `app/app.css`. Recrie a UI fielmente; troque apenas o dado mock por
dados reais da API.

---

## Como rodar o protótipo
Abra `Danzeroum - Buscador de Oportunidades.html` em um servidor estático (ele carrega `app/*` por
caminho relativo e React/Babel via CDN). Navegação por estado React (sem rotas de URL no protótipo —
no app real, use o router do framework). Tema claro/escuro persiste em `localStorage('dz-theme')`.

## Arquitetura do protótipo (mapa de arquivos)
| Arquivo | Conteúdo |
|---|---|
| `Danzeroum - Buscador de Oportunidades.html` | Shell: carrega libs, CSS, todos os `app/*.jsx`, aplica Tweaks, monta `<Root>` |
| `app/app.css` | **Todos os tokens + componentes CSS** (sidebar, topbar, tabela, kanban, badge, gauge, drawer) |
| `app/data.js` | `window.DZ` — dados mock BR + helpers (`fmtBRL`, `daysTo`, `fmtDate`). **Espelha os contratos do tracker** |
| `app/icons.jsx` | `Icons` (set inline), `Logo`, `Reco` (badge), `Gauge` (anel de score) |
| `app/shell.jsx` | `App`, `Sidebar`, `Topbar`, `useTheme`, roteador por estado, `NAV`, `TITLES` |
| `app/screens-core.jsx` | `ScreenDashboard` + `DeadlinePill`, `FitBar`, `SourceTag` |
| `app/screens-list.jsx` | `ScreenList` (tabela filtrável) |
| `app/screens-detail.jsx` | `ScreenDetail` (vitrine: campos + card de score + drawer raw_json) |
| `app/screens-ops.jsx` | `ScreenCollect`, `ScreenAlerts` |
| `app/screens-config.jsx` | `ScreenConfig`, `ScreenDocs`, `ScreenCerts` |
| `app/screens-biz.jsx` | `ScreenProposals` (kanban), `ScreenCalc` (Fator R), `ScreenCRM` |
| `app/tweaks-panel.jsx` | Painel de Tweaks (só protótipo — descartar no app real) |

---

## Screens / Views

> Mapeamento detalhado funcionalidade → tela → arquivo de origem do dado está na **Seção 4 do
> `UI-DESIGN-BRIEF.md`**. Resumo de implementação abaixo.

### Shell (todas as telas)
- **Layout:** grid `244px 1fr`. Sidebar `--bg-2` com 3 grupos (Operação/Negócio/Sistema). Topbar sticky
  60px com título, busca global (340px), sino de alertas, toggle de tema, botão "Coletar".
- **Item de nav:** 8px/11px, raio 9px, ativo = superfície branca + barra de acento 3px à esquerda +
  `count` pill. Ver `.nav-item` em `app/app.css`.
- **Responsivo:** `<880px` colapsa a sidebar (no app real, troque por drawer mobile).

### 1. Painel (Dashboard) — `ScreenDashboard`
- 4 KPI cards (grid 4col): Oportunidades ativas, Recomendadas (GO), A revisar, Pipeline potencial.
- Grid `1.7fr 1fr`: tabela "Top oportunidades por aderência" + coluna direita ("Por recomendação" com
  barras GO/REVIEW/SKIP, "Prazos próximos").
- 4 atalhos no rodapé. **Origem do dado:** `reporting.build_report` (`total`, `por_recomendacao`, `top[]`).

### 2. Oportunidades (Lista) — `ScreenList`
- Card de filtros: chips de recomendação, selects (UF/categoria/fonte), slider `fit mín`, ordenação,
  toggle "mostrar descartados". Tabela densa `.tbl` (objeto, órgão/UF, fonte, valor, fit-bar, prazo, badge).
- Linha clicável → detalhe. **Origem:** `tenders` ⨝ `score`; CLI `list` / `list_scored`.

### 3. Detalhe + Scoring ⭐ — `ScreenDetail`
- Cabeçalho (badge recomendação + fonte + nº + valor + prazo + ações: raw_json, ver no portal, gerar proposta).
- Grid `1fr 1.15fr`: esquerda = campos do edital (lista chave/valor) + checklist `key_requirements`
  (ícone ✓/✗); direita = **card de score** sticky: 3 `Gauge` (fit/risco/complexidade), banner de
  recomendação, `analysis_text`, `pricing_guidance`.
- **Drawer `raw_json`:** overlay direito 720px com `<pre>` do `tenders.raw_json`.
- **Origem:** `SCORE_SCHEMA` (`scoring/schema.py`) + `tenders` + `tenders.raw_json`.

### 4. Coleta — `ScreenCollect`
- Grid `1.3fr 1fr`: painel "Executar coleta" (botão → log animado em terminal escuro + resumo
  `collected/new/scored/alerts/errors`) + "Histórico de execuções" (tabela). Direita: agendador + fontes
  (toggle por fonte, último run, erros). **Origem:** `pipeline.CollectionResult`; CLI `collect`/`schedule`.

### 5. Configuração — `ScreenConfig`
- Grid 2col de seções: Fontes & abrangência (UFs/modalidades como chips, horizonte slider) · Palavras-chave
  (chips editáveis + add) · Pontuação (radio scorer heurístico/LLM, slider `min_fit`) · Agendamento · SMTP.
- **Origem:** `config.py` + `.env.example`.

### 6. Documentos & Certidões — `ScreenDocs`
- Banner de pendência se houver certidão vencida/vencendo. Tabela (documento, tipo, emissor, emissão,
  validade com contagem de dias, situação válido/vencendo/vencido). **Origem:** `documents`.

### 7. Propostas — `ScreenProposals`
- 4 KPI + **kanban arrastável** (HTML5 DnD) com 6 colunas (DRAFT/SENT/UNDER_REVIEW/WIN/LOST/DISQUALIFIED).
  Card = título, edital+versão, valor, validade. **Origem:** `proposals`.

### 8. Calculadora (Fator R) — `ScreenCalc`
- Grid `1fr 1.1fr`: parâmetros (receita, sliders folha/custo/margem) + resultado (preço mínimo em painel
  marinho, breakdown custo/tributos/margem). Fator R ≥ 0,28 → Anexo III, senão Anexo IV. **Origem:** BLUEPRINT.

### 9. CRM / Clientes — `ScreenCRM`
- Funil 4 colunas (qualificação/oportunidade/proposta/cliente) com soma por estágio; card = órgão, contato,
  valor, nº editais. **Origem:** `clients` + `crm/*.json`.

### 10. Atestados — `ScreenCerts`
- Grid 2col de cards (cliente, objeto, valor, ano, volume, tags). **Origem:** `technical_certificates`.

### 11. Alertas — `ScreenAlerts`
- Grid `1.6fr 1fr`: lista de alertas (ícone por tipo, nível de cor, não-lido destacado) + preferências de
  e-mail. **Origem:** `notifications.py`; disparo quando `fit ≥ min_fit` ou janela de vencimento.

---

## Interactions & Behavior
- **Navegação:** estado `route` em `App` (`shell.jsx`). `go(route, payload)` troca de tela e reseta scroll.
  No app real, mapeie para rotas de URL (`/painel`, `/oportunidades`, `/oportunidades/:id`, …).
- **Tema:** `useTheme` alterna a classe `dark` no `<html>` e persiste em `localStorage('dz-theme')`.
- **Drawer raw_json:** scrim + painel animado (`@keyframes drawerIn`); fecha por scrim ou X.
- **Coleta:** `setInterval` simula um pipeline (log linha a linha, barra de progresso) e mostra o resumo.
  No app real → chamar `POST /collect` e exibir streaming/polling do `CollectionResult`.
- **Kanban:** `draggable` + `onDragStart/onDrop` muda o `status` da proposta no estado.
- **Calculadora:** recalcula em tempo real a cada slider (puro derivado, sem rede).
- **Animações:** entrada `fadeUp/fadeIn` **só transform** (conteúdo sempre visível, mesmo sem repaint) e
  gated em `prefers-reduced-motion: no-preference`. Hovers: `translateY(-1/2/3px)` + sombra.

## State Management
Protótipo: tudo em `useState` local + `localStorage` para tema. App real:
- **Servidor:** `tenders` (+ score, raw_json), `documents`, `proposals`, `clients`,
  `technical_certificates`, `config`, `runs/CollectionResult`, `alerts` → via API.
- **Cliente:** filtros da lista, rota atual, tema, estado de drag do kanban, inputs da calculadora.
- **Mutações:** mudar status de proposta, upload de documento, editar config, rodar coleta, marcar alerta lido.

## Design Tokens
Fonte canônica: `brand/tokens.css` (claro+escuro) e `app/app.css` (componentes + semânticas).
- **Marca:** terracota `#bd4e1c` (AA `#b3470f`) · marinho `#24324a` · teal `#0f7d6b`.
- **Semânticas:** GO `#0f7d6b` · REVIEW `#c47915` · SKIP `#8a7a6a` (variantes dark em `app.css`).
- **Neutros (claro):** bg `#fbf7f1`, bg-2 `#f4ece1`, ink `#231a14`, text `#4a3d33`, muted `#7a6a5b`,
  faint `#9c8a78`, line `#e6dccd`, line-2 `#d3c4ae`.
- **Tipografia:** IBM Plex Sans (400–700) + IBM Plex Mono (400–600).
- **Raios:** 6/10/14/18px (multiplicados por `--rscale`). **Easing:** `cubic-bezier(.2,.7,.3,1)`.
- **Densidade de tabela:** `--row-py` (8/12/16). **Badge:** atributo `data-badge` (outline/solid/minimal).

## Assets
- **Marca:** `brand/logo-danzeroum.svg`, `brand/logo-danzeroum-dark.svg`, `brand/favicon.svg`. No protótipo
  o logo é inline (`Logo` em `icons.jsx`) com cores por tema.
- **Ícones:** todos inline em `app/icons.jsx` (`stroke="currentColor"`) — sem dependência de biblioteca.
  Troque pelo icon set do design system do app se houver.
- **Fontes:** Google Fonts (IBM Plex Sans + Mono); self-host recomendado em produção.
- **Tweaks:** `app/tweaks-panel.jsx` é só ferramenta de protótipo — **não portar** para produção.

## Pré-requisito técnico (bloqueador de engenharia)
As telas leem/escrevem dados que hoje só existem via CLI/SQLite. **Antes da UI**, criar uma camada de API
(ex.: **FastAPI** sobre o mesmo core/repo): `GET /tenders`, `GET /tenders/{id}` (+score +raw_json),
`POST /collect`, `GET /report`, `GET/PUT /config`, CRUD de `documents`/`proposals`/`clients`/
`technical_certificates`, `GET /alerts`. Sem ela, o front fica sem dados reais.

## Files
- `Danzeroum - Buscador de Oportunidades.html` — protótipo hi-fi navegável (11 telas).
- `app/` — CSS, dados mock e componentes JSX (ver tabela acima).
- `brand/` — logo (claro/escuro), favicon, `tokens.css`.
- `UI-DESIGN-BRIEF.md` — brief de design: levantamento, mapa de fontes de verdade, inventário de telas,
  IA/navegação, design system, priorização por fase, fluxo de trabalho. **Leia primeiro.**
