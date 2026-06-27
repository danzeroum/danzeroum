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
├── contato.php         # handler do formulário (envia e-mail no VPS)
├── privacidade.html    # Política de Privacidade (LGPD)
├── obrigado.html       # página de agradecimento (alvo do formulário)
├── 404.html
├── robots.txt
├── sitemap.xml
├── .github/workflows/
│   └── deploy.yml      # publica no VPS via SSH/rsync a cada push no main
└── assets/
    ├── styles.css      # design system compartilhado por todas as páginas
    ├── theme.js        # alternância de tema claro/escuro
    ├── projects.js     # dados dos 23 cases + render/filtros (campos: outcome, featured, demo)
    ├── favicon.svg
    └── og-image.png    # card social 1200×630
```

## Contato (WhatsApp + formulário)

- **WhatsApp:** `5511996685998` (links `https://wa.me/5511996685998`).
- **Formulário:** processado por `contato.php` no próprio VPS — envia e-mail para
  `contato@danzeroum.com` e redireciona para `/obrigado.html`. Tem honeypot anti-spam.
  - Requer **PHP** habilitado no host e a função `mail()` funcional (sendmail/postfix no VPS).
  - Ajuste as constantes no topo de `contato.php` (`DESTINO`, `REMETENTE`).
  - Para entrega mais confiável (SPF/DKIM), troque `mail()` por SMTP autenticado via PHPMailer.

> Analytics (opcional): para métricas sem cookie e sem banner LGPD, adicione no `<head>` a tag
> do Plausible ou do Cloudflare Web Analytics.

### Sobre os cases
Os 23 cases em `assets/projects.js` correspondem **exatamente** aos repositórios
**públicos** de `github.com/danzeroum`. Repositórios privados não são listados (e seus
links quebrariam). Para destacar um projeto privado, **torne-o público primeiro** e
adicione o objeto ao array `PROJECTS` com `featured: true`.

## Deploy automático para o VPS Hostinger

O workflow `.github/workflows/deploy.yml` publica o site no VPS **a cada push no `main`**
(e manualmente em *Actions → Run workflow*), via SSH + `rsync`.

### Secrets a configurar (Settings → Secrets and variables → Actions)

| Secret | O que é | Exemplo |
|--------|---------|---------|
| `SSH_HOST` | IP ou host do VPS | `203.0.113.10` |
| `SSH_USER` | usuário SSH | `root` ou um usuário dedicado de deploy |
| `SSH_PORT` | porta SSH (opcional, default `22`) | `22` |
| `SSH_PRIVATE_KEY` | **chave privada** SSH cuja pública está em `~/.ssh/authorized_keys` do VPS | conteúdo do arquivo da chave |
| `DEPLOY_PATH` | web root do site no VPS | `/var/www/danzeroum.com/public_html` |

> ⚠️ O `rsync` usa `--delete`: o servidor fica **idêntico** ao repositório. Aponte `DEPLOY_PATH`
> para o web root **exclusivo do site** (não a home inteira), senão arquivos fora do repo serão
> removidos. Gere uma chave dedicada com `ssh-keygen -t ed25519 -C "deploy-danzeroum"` e adicione
> a pública no VPS.

O DNS de `danzeroum.com` continua apontando para o VPS — **nada de DNS muda** neste fluxo.

## Desenvolvimento local

```bash
# site estático
python3 -m http.server 8000          # http://localhost:8000

# com o formulário PHP funcionando
php -S localhost:8000                 # http://localhost:8000 (requer PHP)
```
