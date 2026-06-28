# Handoff: Projetor de slides por projeto (seção "03 — Projetos")

## Overview
Na seção **03 — Projetos** do portfólio, cada card de projeto deve abrir, **num clique**, uma
**apresentação de slides** (overlay/modal) contando a história daquele projeto — menos técnica,
focada na **oportunidade** que o código oferece, com um slide honesto sobre o estado atual.
O usuário navega pelos slides, **troca para outro projeto sem fechar** e **fecha facilmente**
(X / Esc / clique fora). Inclui também uma **correção de conteúdo** do projeto ConciliaIA.

## About the Design Files
O arquivo deste bundle (`Daniel Lau - Portfolio.html`) é uma **referência de design feita em HTML** —
um protótipo que mostra o visual e o comportamento pretendidos, **não código de produção para copiar
direto**. A tarefa é **recriar este design no ambiente do codebase de destino** (React/Vue/Svelte/etc.),
usando os padrões e a biblioteca de componentes já estabelecidos. Se ainda não houver um ambiente,
escolha o framework mais adequado e implemente lá.

No protótipo, toda a lógica do projetor está num bloco `<script>` inline no fim do `<body>`
(controlador `openProjectDeck`, dados `DECKS`, render por tipo de slide). Use-o como **fonte da verdade
de comportamento e de conteúdo**, não necessariamente como a arquitetura final.

> **Base = versão real do repositório** (`danzeroum.com` / `index.html`): a grade tem **23 projetos**
> com **filtros por categoria** (chips `CATS` + `renderGrid`/`renderChips`) e cada projeto tem campos
> `cat` e `featured`. O projetor de slides foi aplicado **apenas aos 6 projetos em destaque**
> (`featured:true`), que são os que possuem conteúdo de deck escrito. Os demais 17 cards permanecem
> exatamente como hoje (sem gatilho de apresentação) até que se escreva o conteúdo deles.

## Fidelity
**Alta fidelidade (hifi).** Cores, tipografia, espaçamentos, raios e transições são finais e devem ser
reproduzidos fielmente com os componentes do codebase. O conteúdo textual dos slides é final.

---

## Screens / Views

### 1. Card do projeto (gatilho) — já existe, recebe ajustes
- **Purpose**: cartão na grade de projetos; agora também abre a apresentação.
- **Gating**: o gatilho (clicável + dica) só aparece quando **existe deck para aquele projeto**
  (`window.DECKS[p.slug]`). Na base atual, isso vale só para os 6 `featured`. A grade é
  **re-renderizada** ao trocar de filtro, então o gatilho deve ser recalculado dentro de `cardHTML`
  a cada render (não dependa de marcar o DOM só no load).
- **Layout**: card existente (`.card`), grid de 1 col (mobile) / 2 cols (`min-width:680px`), `gap:16px`.
- **Ajustes necessários**:
  - O card inteiro vira clicável (`cursor:pointer`, `role="button"`, `tabindex="0"`,
    `aria-label="Abrir apresentação de <nome>"`), guardando o identificador do projeto (`data-slug`).
  - Adicionar, na linha de links inferior (`.clinks`), uma **dica** à esquerda:
    ícone "play" + texto **"Ver apresentação"**, na cor da marca (`--brand-ink`, `font-weight:600`),
    com `margin-right:auto` para empurrar os links de demo/repo para a direita.
  - **Importante**: clicar nos links reais (Ver demo / Repositório) **não** abre o deck — o handler
    ignora cliques que caem dentro de um `<a>` (`event.target.closest('a')`).
  - Teclado: Enter/Espaço sobre o card abre o deck (ignorando foco em links internos).

### 2. Projetor de slides (overlay) — NOVO
- **Purpose**: apresentar 6 slides do projeto selecionado.
- **Layout**:
  - `.deckwrap`: `position:fixed; inset:0; z-index:1000; display:flex; align-items:center;
    justify-content:center; padding:clamp(12px,3vw,32px)`. Oculto por padrão (`display:none`),
    visível com a classe `show`.
  - `.deck-scrim`: backdrop `position:absolute; inset:0`,
    `background:color-mix(in srgb,#0c0703 78%,transparent)` (dark: `#000 80%`),
    `backdrop-filter:blur(7px)`. Clicar nele fecha.
  - `.deck-panel`: `width:min(960px,100%); max-height:min(680px,calc(100vh - 32px));
    display:flex; flex-direction:column; background:var(--bg); border:1px solid var(--line-2);
    border-radius:20px; overflow:hidden; box-shadow:0 40px 120px -30px rgba(0,0,0,.65)`.
    `role="dialog" aria-modal="true"`.
  - Estrutura interna do painel (3 faixas):
    1. **`.deck-top`** (header): `padding:14px 14px 14px 18px; border-bottom:1px solid var(--line)`.
       Contém o **switcher** (`.deck-switch`, faixa horizontal rolável de pílulas, uma por projeto)
       e o **botão fechar** (`.deck-x`, 38×38, ícone X).
    2. **`.deck-stagearea`** (palco): `flex:1; overflow-y:auto; padding:clamp(28px,4.5vw,52px)`.
       Renderiza um slide por vez.
    3. **`.deck-nav`** (rodapé): `padding:14px 18px; border-top:1px solid var(--line)`. Contém
       seta anterior (`.deck-arrow`, 42×42), **dots** (`.deck-dots`, centralizados, `flex:1`) e
       seta próxima.
- **Trava de scroll**: ao abrir, adicionar `deck-lock` no `<html>` (`overflow:hidden`); remover ao fechar.

#### Pílulas do switcher (`.deck-pill`)
- Mono, `.72rem`, `border:1px solid var(--line)`, `border-radius:999px`, `padding:6px 13px`,
  `white-space:nowrap`. Ativa (`.on`): `color:var(--on-brand); background:var(--brand); border-color:var(--brand)`.
- Clicar numa pílula **abre o deck daquele projeto** (reinicia no slide 1).
- A faixa rola horizontalmente sem barra visível (`scrollbar-width:none`).

#### Dots (`.deck-dot`)
- `8×8`, círculo, `background:var(--line-2)`. Ativo (`.on`): `background:var(--brand); transform:scale(1.35)`.
- Um dot por slide (total = nº de slides do projeto, **6**). Clicável → vai ao slide.

#### Setas (`.deck-arrow`)
- `42×42`, `border:1px solid var(--line-2)`, `border-radius:11px`. `:disabled` → `opacity:.32`.
- A seta "anterior" fica desabilitada no slide 1; a "próxima" no último slide.

---

## Tipos de slide (layouts)
Cada deck é uma sequência de **6 slides** de 4 tipos. Largura de conteúdo `max-width:760px`,
centralizada. Entrada anima **apenas o deslocamento** (`translateY(12px)→0`, 0.4s) — **nunca a
opacidade** (o conteúdo deve estar visível por padrão mesmo sem animação).

1. **`cover`** (capa): linha de tag (mono, terracota, pill) + status (mono, com bolinha teal);
   nome do projeto grande (`.ds-name`, `clamp(2.4rem,5.2vw,3.7rem)`, `font-weight:600`, `letter-spacing:-.03em`);
   frase-gancho (`.ds-line`, `clamp(1.15rem,2vw,1.5rem)`, `max-width:24ch`); rodapé `danzeroum/<slug>` (mono, faint).
2. **`lead`** (narrativa): rótulo (mono, terracota, uppercase, `letter-spacing:.16em`) + título
   (`.ds-title`, `clamp(1.7rem,3.4vw,2.5rem)`, `line-height:1.12`) + parágrafo (`.ds-body`,
   `clamp(1.02rem,1.5vw,1.2rem)`, `color:var(--text)`, `max-width:62ch`) + contador "NN / NN" (mono, faint).
3. **`list`** (oferta / para quem): rótulo + título menor (`.ds-title.sm`) + lista de itens.
   Cada item: `<strong>` (título, `color:var(--ink)`, `1.06rem`) + `<span>` (descrição, `color:var(--muted)`).
   Em `min-width:640px` cada item vira 2 colunas: `minmax(190px,38%) 1fr`, `gap:18px`, com borda-topo
   `1px solid var(--line)` separando os itens.
4. **`honest`** (estado atual): rótulo + título menor + lista de pontos; cada ponto com um **selo
   circular** com check (`.ds-chk`, 26×26, `color:var(--accent)`, `background:color-mix(in srgb,var(--accent) 12%,transparent)`).
5. **`cta`** (último slide, montado a partir dos metadados): rótulo "Veja por conta própria" +
   título "Código aberto. Demo no ar. Sem caixa-preta." + parágrafo + dois botões:
   **primário** (`.ds-btn.primary`, `background:var(--brand)`, texto `--on-brand`) "Ver demo ao vivo"
   (só se houver demo) e **fantasma** (`.ds-btn.ghost`) "Ver o código" (GitHub). Botões abrem em nova aba.

> O slide `cover` e o `cta` **leem nome/tag/status/demo/gh dos metadados do projeto** (array
> `PROJECTS` já existente) — não duplique esses campos no conteúdo dos slides.

---

## Interactions & Behavior
- **Abrir**: clique/Enter/Espaço no card → `open(slug)`. Define slide 0, monta dots, marca a pílula
  ativa, adiciona `show` + `deck-lock`, foca o painel.
- **Navegar**: setas, dots, e teclado — `ArrowRight`/`ArrowLeft` (±1), `Home` (primeiro),
  `End` (último). `go(n)` faz clamp em `[0, total-1]`.
- **Trocar de projeto**: clicar numa pílula chama `open(outroSlug)` (reinicia no slide 1, sem fechar).
- **Fechar**: botão X, `Escape`, ou clique no scrim/fora do painel → `close()`. Remove `show` e
  `deck-lock`; **devolve o foco** ao elemento que abriu (acessibilidade).
- **Animações**: painel entra com `dkpop` (0.32s, leve `translateY` + scale); slide entra com
  `dkslide` (0.4s, só translate). Respeitar `@media (prefers-reduced-motion: reduce)` → sem animações.
- **Estado dos controles**: setas desabilitam nos extremos; dot ativo acompanha o índice.

## State Management
- `slug` atual, índice `i` do slide, lista de slides do projeto, e `lastFocus` (para restaurar foco).
- Total de slides = `DECKS[slug].length` (5 de conteúdo) **+ 1** (o slide `cta` gerado) = **6**.
- Sem fetch: todo o conteúdo é estático (mapa `DECKS` keyed por `slug`).

---

## ⚠️ Correção de conteúdo — ConciliaIA (FAZER)
O card atual descreve ConciliaIA como **"ambiente virtual de conciliação de acordos / litígios"**
com a tag **"LegalTech · Conciliação"**. **Isto está errado.** O repositório real
(`danzeroum/ConciliaIA`) é **reconciliação financeira** para e-commerce/varejo: concilia as vendas
do lojista com os relatórios das adquirentes (Cielo, Rede, Stone) e detecta divergências
(MDR/taxa, NSU/registro ausente, chargeback, atraso de liquidação), com importação CSV/EDI,
reconciliação assíncrona, dashboard e API versionada.

**Atualizar o registro do projeto (objeto em `PROJECTS`) para:**
- `cat`: `fintech` (era `legal`) — passa a aparecer sob o filtro **FinTech**, não LegalTech.
- `tag`: `FinTech · Conciliação` (era `LegalTech · Conciliação`)
- `desc`: `Reconciliação financeira para e-commerce e varejo: concilia as vendas do lojista com os
  relatórios das adquirentes (Cielo, Rede, Stone) e detecta divergências — taxa (MDR), registro
  ausente, chargeback e atraso de liquidação — numa API versionada e num dashboard.`
- `tech`: `['Python','FastAPI','PostgreSQL','React']` (era `['Python','LLM','Web']`)
- `status`, `demo`, `gh`: inalterados.

O conteúdo do **deck** do ConciliaIA já reflete a versão correta (ver abaixo).

---

## Conteúdo dos decks (fonte da verdade — 6 projetos)
Cada projeto: capa (frase-gancho) → A oportunidade (lead) → O que oferece (list) →
Para quem (list) → Onde está hoje / honesto (honest) → CTA (gerado). Textos finais, em PT-BR.

> O bloco `DECKS` completo (com todos os títulos, itens e descrições) está no `<script>` inline do
> arquivo HTML deste bundle. Reaproveite-o verbatim. Resumo das frases-gancho de capa:
> - **btvChatCorp** — "A inteligência da sua empresa, sem mandar um dado sequer para fora."
> - **BuildToValue Governance** — "Quando a IA toma uma decisão, alguém vai pedir a prova. Aqui ela já existe."
> - **Central de Inteligência Jurídica** — "Vários especialistas jurídicos trabalhando juntos — sob o seu comando."
> - **ConciliaIA** — "Vendeu pela maquininha. Mas recebeu tudo o que era seu?"
> - **CriptoTrade** — "Um robô de trading que pede licença antes de arriscar o seu dinheiro."
> - **ExecutAgent** — "Descreva a tarefa. Receba o entregável. Com números que você pode confiar."

**Diretriz editorial (manter):** honestidade. Os slides "Onde está hoje" declaram limites reais —
ex.: CriptoTrade roda em paper trading/dry-run (zero conexão real à corretora); Governance tem
~15% de falso positivo não validado externamente e gateway sem TLS por padrão; demos rodando na VPS
mas ainda não em uso por clientes. Não inflar.

---

## Design Tokens (já existentes no portfólio — reutilizar)
Cores (tema claro / escuro via `html.dark`):
- `--bg` `#fbf7f1` / `#141009` · `--bg-2` `#f4ece1` / `#1d160e`
- `--ink` `#231a14` / `#f6ede1` · `--text` `#4a3d33` / `#d6c6b4`
- `--muted` `#7a6a5b` / `#a8957f` · `--faint` `#9c8a78` / `#82705d`
- `--line` `#e6dccd` / `#2e2418` · `--line-2` `#d3c4ae` / `#41331f`
- `--brand` `#bd4e1c` / `#e8772f` · `--brand-ink` `#b3470f` / `#f0934d`
- `--accent` `#0f7d6b` / `#36c0a4` · `--on-brand` `#fff8f1` / `#1a1106`

Tipografia: **IBM Plex Sans** (texto) e **IBM Plex Mono** (rótulos/tags/contadores/slug).
Raios: cards 16px · painel 20px · botões/setas 11px · pílulas 999px · selo de check 50%.
Easing: `--ease: cubic-bezier(.2,.7,.3,1)`. z-index do overlay: 1000.
Sombra do painel: `0 40px 120px -30px rgba(0,0,0,.65)`.

## Assets
- Ícones (X, setas, link externo, GitHub, check, play): **SVG inline**, `currentColor`. Sem libs externas.
- Nenhuma imagem nova. Fontes via Google Fonts (já incluídas no `<head>`).

## Files
- `Daniel Lau - Portfolio.html` — protótipo completo. A feature está:
  - **CSS**: bloco "PROJETOR DE SLIDES" no fim do `<style>`.
  - **Markup do card**: template string da função que monta `#grid` (no 1º `<script>`), com
    `data-slug`, `role/tabindex` e a dica `.clink.cue`.
  - **Controlador + dados**: 2º `<script>` inline ("Projetor de slides por projeto") — `DECKS`,
    render por tipo, `open/go/close`, switcher, dots, teclado, wireCards (delegação em `#grid`).
