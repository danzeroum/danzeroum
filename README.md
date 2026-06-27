# Danzeroum — site comercial + portfólio

Site institucional da **Danzeroum**, estúdio de engenharia de IA e software sob medida
para médias empresas. Mistura uma **landing comercial** (serviços, processo, diferenciais,
modelos de engajamento, FAQ, conversão) com um **portfólio** de cases reais validados a
partir dos repositórios públicos em [github.com/danzeroum](https://github.com/danzeroum).

> Produção: **https://danzeroum.com**

## Stack

HTML/CSS/JS **estático, sem build e sem dependências de runtime** (só Google Fonts).
Design system "golden hour" (terracota + teal), tema claro/escuro persistido, mobile-first,
acessível. Qualquer hospedagem de arquivos estáticos serve o site como está.

## Estrutura

```
.
├── index.html          # landing comercial + cases
├── privacidade.html    # Política de Privacidade (LGPD)
├── obrigado.html       # página de agradecimento (alvo do formulário)
├── 404.html
├── robots.txt
├── sitemap.xml
└── assets/
    ├── styles.css      # design system compartilhado por todas as páginas
    ├── theme.js        # alternância de tema claro/escuro
    ├── projects.js     # dados dos 23 cases + render/filtros (campos: outcome, featured, demo)
    ├── favicon.svg
    └── og-image.png    # card social 1200×630
```

## Antes de publicar — preencher placeholders

Há marcadores propositais para você substituir pelos dados reais:

| Onde | Placeholder | Trocar por |
|------|-------------|-----------|
| `index.html`, `obrigado.html` | `wa.me/55XXXXXXXXXXX` | número real de WhatsApp (DDI 55 + DDD + número) |
| `index.html` (form `action`) | `https://formspree.io/f/SEU_ID` | endpoint real do Formspree (ou trocar pelo Netlify Forms) |
| `index.html`, `privacidade.html` | `contato@danzeroum.com` | e-mail de contato real, se diferente |
| `index.html` (`<head>`) | — | opcional: tag de analytics sem cookie (Plausible / Cloudflare Web Analytics) |

### Sobre os cases
Os 23 cases em `assets/projects.js` correspondem **exatamente** aos repositórios
**públicos** de `github.com/danzeroum`. Repositórios privados não são listados (e seus
links quebrariam). Para destacar um projeto privado, **torne-o público primeiro** e
adicione o objeto ao array `PROJECTS` com `featured: true`.

## Deploy

O site é estático e host-agnóstico. Recomendado: publicar em **preview** primeiro, validar
e só então promover para `danzeroum.com`.

- **GitHub Pages:** crie um arquivo `CNAME` na raiz com `danzeroum.com` e ative Pages na branch.
- **Cloudflare Pages / Netlify / Vercel:** aponte o projeto para esta raiz; sem comando de build,
  diretório de saída = raiz (`/`). Configure o domínio no painel do host.

## Desenvolvimento local

```bash
python3 -m http.server 8000   # depois abra http://localhost:8000
```
