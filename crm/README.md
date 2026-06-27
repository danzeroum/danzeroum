# CRM flat-file da Danzeroum

CRM leve, versionado em git, para acompanhar prospecção de leads a partir dos cases/repos.

## Modelo de privacidade (importante)

Este repositório é **público**. Por isso:

- **Versionado (sem dado pessoal):** `targets.json` (matriz de alvos), `queries.json` (URLs de busca
  geradas, sem nomes) e `pipeline.json` (contagens agregadas).
- **NÃO versionado (dados pessoais):** `leads.private.json` — onde você preenche nome, empresa e
  contatos reais. Está no `.gitignore` e **nunca** deve ir para o git público.

> Não commite dados pessoais de terceiros aqui. Se quiser versionar leads reais com histórico,
> use um **repositório privado** separado. Star/seguidor ≠ consentimento de contato; faça outreach
> de forma manual e moderada (a AUP do GitHub proíbe mensagens não solicitadas em massa).

## Arquivos

| Arquivo | Conteúdo | Versionado? |
|---------|----------|-------------|
| `targets.json` | Cargos-alvo, setores, keywords e templates por case | ✅ sim (sem PII) |
| `queries.json` | URLs de busca do LinkedIn geradas por (case, cargo, setor) | ✅ sim (sem PII) |
| `pipeline.json` | Resumo do funil por status | ✅ sim (sem PII) |
| `leads.private.json` | Leads reais (nome, empresa, contato, status) | ❌ não — **gitignored** |
| `leads.example.json` | Schema de exemplo do arquivo privado | ✅ sim (fake) |

## Uso

```bash
pip install requests
python scripts/crm_collector.py            # gera queries.json + pipeline.json (sem PII)
python scripts/crm_collector.py --stargazers   # opcional: coleta stargazers -> leads.private.json (local)
```

Fluxo: rode o collector → abra `queries.json`, pesquise os alvos no LinkedIn → registre os leads
reais em `leads.private.json` (copie de `leads.example.json`) → atualize o `status` conforme avança
(`novo → contatado → respondeu → demo → fechado`).

O workflow `.github/workflows/crm_collect.yml` regenera os arquivos **não-pessoais** periodicamente
e faz commit automático — sem tocar em `leads.private.json`.
