# 🏗️ BLUEPRINT — Sistema de Gestão Danzeroum: Buscador de Oportunidades Públicas

**Arquivo:** `docs/buscador-oportunidades/BLUEPRINT.md` · **Versão:** 1.0 (consolidada)

> Documento estratégico e técnico. **Não contém código de produção** — os trechos de SQL/Python são **ilustrativos**, para comunicar o design. Implementação prevista para a próxima rodada (V1).

---

## 1. Visão Geral

### 🎯 Missão

Construir um **rastreador de oportunidades públicas** para a Danzeroum Tecnologia da Informação LTDA (CNPJ 35.674.569/0001-17), que consolida editais de TI de múltiplos portais governamentais, aplica análise inteligente via LLM e entrega ao sócio-administrador uma lista priorizada de licitações — com risco, adequação e recomendação — reduzindo tempo de prospecção e aumentando a taxa de conversão em contratos.

### 📋 Escopo da V1 (MVP)

| Módulo | Status | Observação |
|---|---|---|
| **Monitoramento de Licitações** | ✅ PoC (V1) | Adaptadores: PNCP (prioritário), Compras.gov, Compras SP, Prefeitura SP |
| **Motor de Scoring com LLM** | ✅ Blueprint | Camada agnóstica ao provedor; saída JSON estruturada |
| **Gestão de Documentação** | ✅ Blueprint | Certidões, atestados técnicos, contrato social |
| **Modelo de Precificação** | ✅ Blueprint | Calculadora de preço mínimo (Fator R / Simples vs Lucro Presumido) |
| **Integração com CRM** | ⚠️ V2 | Reaproveitar `scripts/crm_collector.py` e `crm/*.json` |
| **Dashboard Web** | ⚠️ V3 | React/Vue + Chart.js |
| **Automação de Propostas** | ⚠️ V4 | Geração de PDF + envio automatizado |

---

## 2. Vantagens Competitivas da Danzeroum

### ✅ O que a empresa já tem a seu favor

| Vantagem | Detalhe |
|---|---|
| **ME no Simples Nacional** | Carga tributária reduzida → preço competitivo em pregões. Fator R pode ser planejado para migrar ao Anexo III (a partir de 6%). |
| **6+ anos de atividade** | Fundada em 02/12/2019 → maturidade cadastral que transmite confiança em habilitações. |
| **CNAEs de TI alinhados** | 6209-1/00 (suporte), 6204-0/00 (consultoria), 6311-9/00 (dados/hospedagem) — cobrem a maioria dos editais de TI. |
| **Sociedade Limitada** | Responsabilidade limitada ao capital social — estrutura aceita em habilitações. |
| **Dogfooding estratégico** | Construir a própria ferramenta é **prova de capacidade técnica** para clientes públicos e privados. |

### ⚠️ Ressalvas a corrigir antes de escalar

| Ponto de atenção | Ação recomendada |
|---|---|
| **Capital social de R$ 3.000** | Aumentar para **R$ 30.000–50.000** via alteração contratual — muitos editais exigem capital mínimo proporcional ao valor do contrato. |
| **Sem e-CNPJ/e-CPF configurados** | Adquirir certificado digital A1 (arquivo) ou A3 (token) para empresa e sócio-administrador. |
| **Certidões sem monitoramento** | Implementar alerta de vencimento (CND Federal, CRF Simples, FGTS, Estadual, Municipal). |
| **Poucos atestados técnicos** | Solicitar declarações de clientes privados; registrar projetos concluídos no CRM. |

---

## 3. Tipos de Contrato e Elegibilidade

### 📋 O que a Danzeroum pode contratar

**Setor Privado (B2B):**

| Tipo | Exemplo |
|---|---|
| Suporte técnico | Help desk terceirizado, manutenção de infraestrutura |
| Consultoria em TI | Diagnóstico e planejamento de arquitetura tecnológica |
| Hospedagem e tratamento de dados | Cloud hosting, backup gerenciado, processamento de dados |
| Desenvolvimento sob demanda | Software customizado para clientes |
| Contratos recorrentes | Manutenção mensal, monitoramento 24/7 |

**Setor Público (via licitação) — sim, a empresa pode participar:**

| Modalidade | Faixa de valor | Vantagem ME/EPP |
|---|---|---|
| **Dispensa Eletrônica** | Até R$ 50 mil (serviços comuns) | Contratação direta, sem licitação formal |
| **Pregão Eletrônico** | Qualquer valor (mais comum em TI) | Empate ficto + itens exclusivos ME/EPP até R$ 80 mil |
| **Concorrência** | Contratos maiores | Cota de 25% para ME/EPP em itens divisíveis |
| **Registro de Preços (IRP)** | Compra futura por órgão público | Participação em atas para fornecimento contínuo |

### ✅ Requisitos operacionais para licitar

1. **e-CNPJ** (A1 ou A3) — assinatura digital de propostas.
2. **Cadastro no Compras.gov.br** — UASG, senha e certificado.
3. **SICAF** — habilitação prévia para órgãos federais.
4. **Certidões válidas** — CND Federal, CRF Simples, FGTS, Estadual, Municipal.
5. **Atestados técnicos** — comprovação de experiência compatível com o objeto.

---

## 4. Arquitetura do Sistema

### 🗺️ Visão em camadas

```
┌──────────────────────────────────────────────────────────┐
│              📊 DASHBOARD (React/Vue SPA)                 │
├──────────────────────────────────────────────────────────┤
│              🔑 API Gateway (FastAPI)                     │
├──────────────────────────────────────────────────────────┤
│   🧠  MÓDULOS DE NEGÓCIO                                  │
│   │── Monitoramento de Licitações (adaptadores)           │
│   │── Scoring com LLM (análise de editais)                │
│   │── Gestão de Documentos                                │
│   │── Calculadora de Precificação                         │
│   │── CRM (integração V2)                                 │
├──────────────────────────────────────────────────────────┤
│   🛢️  SERVIÇOS DE INFRA                                   │
│   │── PostgreSQL (dados normalizados)                     │
│   │── Redis (cache + fila de tarefas)                     │
│   │── Celery (agendamento de coletas)                     │
│   │── MinIO/S3 (armazenamento de documentos)              │
├──────────────────────────────────────────────────────────┤
│   🌐  FONTES EXTERNAS                                     │
│   │── PNCP (API REST oficial)                             │
│   │── Compras.gov.br (API SIASG / dados abertos)          │
│   │── Compras SP / BEC (scraping)                         │
│   │── Prefeitura SP (e-Negócios / scraping)               │
│   │── Provedores de LLM (agnóstico — ver §7)              │
└──────────────────────────────────────────────────────────┘
```

### 🧩 Padrão Hexagonal (Ports & Adapters)

```
          ┌──────────────────────────────┐
          │      CORE DO SISTEMA          │
          │  (regras de negócio           │
          │   agnósticas às fontes)       │
          │  ┌──────────────────────┐     │
          │  │  Service Layer       │     │
          │  │  - busca_tenders()   │     │
          │  │  - score_tender()    │     │
          │  │  - validate_docs()   │     │
          │  └──────────────────────┘     │
          └──────────┬───────────────────┘
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│ ADAPTADOR│   │ ADAPTADOR│   │ ADAPTADOR│
│   PNCP   │   │ Compras  │   │ Compras  │
│  (API)   │   │  Gov.br  │   │   SP     │
│          │   │  (API)   │   │(Scraping)│
└──────────┘   └──────────┘   └──────────┘
```

**Princípio:** o Core não conhece as fontes externas. Cada adaptador implementa a mesma interface (`fetch_tenders`, `parse_tender`). Adicionar/remover fontes não toca na lógica de negócio.

---

## 5. Modelo de Dados (PostgreSQL)

> SQL ilustrativo do schema canônico para o qual cada adaptador normaliza.

```sql
-- LICITAÇÕES (normalizadas de todas as fontes)
CREATE TABLE tenders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(20) NOT NULL,          -- 'PNCP', 'COMPRAS_GOV', 'COMPRAS_SP', 'PREF_SP'
    external_id VARCHAR(50) NOT NULL,     -- ID nativo do portal de origem
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20),                   -- 'OPEN', 'CLOSED', 'AWARDED', 'CANCELLED'
    category VARCHAR(30),                 -- 'TI', 'TELECOM', 'SOFTWARE', 'INFRAESTRUTURA'
    budget_estimate NUMERIC(12,2),
    value_awarded NUMERIC(12,2),          -- se já houve adjudicação
    publish_date TIMESTAMP,
    deadline TIMESTAMP,
    url VARCHAR(255),
    raw_json JSONB,                       -- payload bruto da fonte (debug/auditoria)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source, external_id)           -- dedupe por origem
);

CREATE INDEX idx_tenders_status   ON tenders(status);
CREATE INDEX idx_tenders_deadline ON tenders(deadline);
CREATE INDEX idx_tenders_category ON tenders(category, status);
CREATE INDEX idx_tenders_fts      ON tenders
    USING gin(to_tsvector('portuguese', coalesce(title,'') || ' ' || coalesce(description,'')));
```

```sql
-- DOCUMENTOS DA EMPRESA
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(30) NOT NULL,            -- 'CND', 'CRF', 'FGTS', 'CERTIDAO_ESTADUAL', 'ATESTADO_TECNICO'
    subtype VARCHAR(30),                  -- ex: 'CND Federal', 'CND Trabalhista'
    name VARCHAR(100),
    file_path VARCHAR(255),
    issue_date DATE,
    expiry_date DATE,
    is_valid BOOLEAN GENERATED ALWAYS AS
        (expiry_date IS NULL OR expiry_date > CURRENT_DATE) STORED,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

```sql
-- PROPOSTAS ENVIADAS
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tender_id UUID NOT NULL REFERENCES tenders(id),
    submitted_at TIMESTAMP,
    status VARCHAR(20),                   -- 'SENT', 'UNDER_REVIEW', 'WIN', 'LOST', 'DISQUALIFIED'
    price_offered NUMERIC(12,2),
    validity_days INT,
    version INT DEFAULT 1,
    notes TEXT
);
```

```sql
-- SCORING DE LICITAÇÕES (resultado da análise LLM)
CREATE TABLE tender_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tender_id UUID NOT NULL REFERENCES tenders(id),
    risk_score NUMERIC(3,2) CHECK (risk_score BETWEEN 0 AND 1),
    fit_score NUMERIC(3,2) CHECK (fit_score BETWEEN 0 AND 1),
    complexity_score NUMERIC(3,2) CHECK (complexity_score BETWEEN 0 AND 1),
    recommendation VARCHAR(10) CHECK (recommendation IN ('GO', 'REVIEW', 'SKIP')),
    key_requirements JSONB,               -- requisitos críticos extraídos do edital
    pricing_guidance TEXT,                -- sugestão de faixa de preço
    analysis_text TEXT,                   -- resumo livre do LLM
    analyzed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tender_scores_fit ON tender_scores(fit_score DESC);
```

```sql
-- ATESTADOS TÉCNICOS (para habilitação)
CREATE TABLE technical_certificates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_name VARCHAR(100),
    project_description VARCHAR(255),
    start_date DATE,
    end_date DATE,
    project_value NUMERIC(12,2),
    scope TEXT,
    file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

```sql
-- CLIENTES (CRM — a evoluir a partir de crm/*.json)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(20) DEFAULT 'INTERNAL',
    name VARCHAR(100),
    type VARCHAR(20),                     -- 'PUBLIC', 'PRIVATE', 'LEAD'
    cnpj VARCHAR(14),
    contact_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(30),
    status VARCHAR(20),                   -- 'LEAD', 'CLIENT', 'ARCHIVED'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_interaction TIMESTAMP
);
```

---

## 6. Adaptadores — Viabilidade por Fonte

| Fonte | Tipo de Acesso | Esforço Estimado | Fragilidade | Prioridade |
|---|---|---|---|---|
| **PNCP** | ✅ API REST oficial (JSON) | Baixo (1–2 semanas) | Baixa | **1ª** |
| **Compras.gov.br** | ✅ API de dados abertos (SIASG) | Baixo–Médio (~2 semanas) | Baixa | **2ª** |
| **Compras SP (BEC)** | ⚠️ Scraping HTML (sem API pública) | Médio (3–4 semanas) | Alta | **3ª** |
| **Prefeitura SP (e-Negócios)** | ⚠️ Scraping HTML + login | Médio–Alto (3–5 semanas) | Alta | **4ª** |

> Estratégia: começar pelo **PNCP** (API oficial, consolida União/estados/municípios) e só descer para scraping nas fontes sem API. Sempre preferir API a scraping para reduzir manutenção.

### 🔄 Fluxo de coleta (todos os adaptadores)

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  AGENDADOR   │──▶│  ADAPTADOR   │──▶│  PARSER /    │──▶│ NORMALIZADOR │
│ (Celery Beat │   │ (fonte-esp.) │   │  VALIDADOR   │   │ (schema      │
│  ou GitHub   │   │  fetch()     │   │ (JSON Schema)│   │  tenders)    │
│  Actions)    │   │              │   │  validate()  │   │  save()      │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
        │                                                       │
        ▼                                                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                 POSTGRESQL → Gatilho → Notificação                    │
│   (novo tender → webhook → dashboard → e-mail ao sócio)               │
└──────────────────────────────────────────────────────────────────────┘
```

### 🧩 Esqueleto ilustrativo — Adaptador PNCP

> ⚠️ **Não é código de produção.** Apenas ilustra a interface. Endpoints/campos exatos devem ser confirmados na documentação oficial da API do PNCP antes da implementação (ver Referências).

```python
from typing import List, Dict, Any
from datetime import datetime
import requests


class PNCPError(Exception):
    pass


class PNCPAdapter:
    """Adaptador para a API do PNCP. Retorna dados normalizados para o core."""

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Accept": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def fetch_open_tenders(
        self,
        keywords: List[str],
        uf: str = "SP",
        page: int = 1,
        per_page: int = 50,
    ) -> Dict[str, Any]:
        """Busca editais com propostas abertas no PNCP."""
        params = {
            "status": "propostas_abertas",
            "uf": uf,
            "palavras_chave": ",".join(keywords),
            "pagina": page,
            "itens_por_pagina": per_page,
        }
        try:
            resp = requests.get(
                f"{self.base_url}/editais",
                params=params,
                headers=self.headers,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise PNCPError(f"Erro na API PNCP: {e}") from e

    def parse_tender(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia o JSON do PNCP para o schema interno 'tenders'."""
        return {
            "source": "PNCP",
            "external_id": str(raw.get("id")),
            "title": (raw.get("objeto") or "")[:255],
            "description": raw.get("descricao_geral") or raw.get("objeto"),
            "status": self._map_status(raw.get("status")),
            "category": self._infer_category(raw.get("objeto", "")),
            "budget_estimate": self._safe_float(raw.get("valor_estimado")),
            "publish_date": self._parse_datetime(raw.get("data_publicacao")),
            "deadline": self._parse_datetime(raw.get("data_limite_proposta")),
            "url": raw.get("url_edital"),
            "raw_json": raw,
        }

    def _map_status(self, status: str | None) -> str:
        mapping = {
            "em_andamento": "OPEN",
            "propostas_abertas": "OPEN",
            "adjudicado": "AWARDED",
            "encerrado": "CLOSED",
            "cancelado": "CANCELLED",
        }
        return mapping.get((status or "").lower(), (status or "").upper())

    def _infer_category(self, title: str) -> str:
        t = title.lower()
        if any(k in t for k in ["tecnologia", " ti", "informaç", "informatica",
                                 "software", "dados", "hospedagem"]):
            return "TI"
        if any(k in t for k in ["telecom", "internet", "rede", "fibra"]):
            return "TELECOM"
        return "OUTROS"

    @staticmethod
    def _safe_float(value):
        try:
            return float(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_datetime(value: str | None):
        if not value:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
```

---

## 7. Motor de Scoring com LLM (agnóstico ao provedor)

### 🤖 Pipeline de análise

```
┌──────────────────────────────────────────────┐
│            ENGENHARIA DE PROMPT                │
│  System: "Você é um especialista em            │
│  licitações públicas de TI. Analise o edital   │
│  e responda em JSON válido conforme o schema." │
│  User: objeto + texto do edital + perguntas    │
│        (risk/fit/complexity/recommendation/...) │
└───────────────────────┬────────────────────────┘
                        ▼
            ┌─────────────────────────┐
            │   PROVEDOR DE LLM       │
            │  (interface agnóstica)  │
            │  OpenAI · Gemini ·      │
            │  Claude · Ollama (local)│
            └──────────┬──────────────┘
                       ▼
            ┌─────────────────────────┐
            │  VALIDAÇÃO JSON Schema  │
            └──────────┬──────────────┘
                       ▼
            ┌─────────────────────────┐
            │  SALVA EM tender_scores │
            │  → Gatilho de notificação│
            └─────────────────────────┘
```

### 📋 Interface agnóstica do LLM

```python
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface única — o core não conhece o provedor concreto."""

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1200,
    ) -> str:
        """Envia o prompt e retorna a resposta bruta (string JSON)."""


class OpenAILLMProvider(LLMProvider):
    ...   # via SDK OpenAI


class GeminiLLMProvider(LLMProvider):
    ...   # via Google Gemini


class ClaudeLLMProvider(LLMProvider):
    ...   # via Anthropic


class OllamaLLMProvider(LLMProvider):
    ...   # via Ollama local (Docker)


# No core:
# provider = OllamaLLMProvider() if cfg.USE_LOCAL_LLM else OpenAILLMProvider()
# raw = provider.complete(system_prompt, user_prompt)
```

### 📤 Saída estruturada (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Tender Scoring Result",
  "type": "object",
  "properties": {
    "risk_score":       { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "fit_score":        { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "complexity_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "recommendation":   { "type": "string", "enum": ["GO", "REVIEW", "SKIP"] },
    "key_requirements": { "type": "array", "items": { "type": "string" } },
    "pricing_guidance": { "type": "string" }
  },
  "required": ["risk_score", "fit_score", "complexity_score",
               "recommendation", "key_requirements"]
}
```

> **Decisão desta rodada:** a escolha do provedor de LLM e a precificação por chamada (custo por edital) **não são aprofundadas aqui** — serão decididas em rodada futura. A arquitetura já isola essa decisão atrás da interface `LLMProvider`.

---

## 8. Modelo de Precificação (Calculadora de Preço Mínimo)

> Precificação **de propostas/serviços** da Danzeroum — distinta de custo de LLM.

```
┌─────────────────────────────────────────────────────┐
│              ENTRADAS DO CÁLCULO                     │
│  📌 Faturamento bruto (últimos 12 meses)            │
│  📌 Folha de pagamento (últimos 12 meses)           │
│  📌 Custo direto do serviço (horas, infra, terceiros)│
│  📌 Margem desejada (%)                             │
│  📌 Tipo de cliente: público ou privado             │
│  📌 Município do cliente (ISS: 2% a 5%)             │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│          MOTOR DE TRIBUTAÇÃO                         │
│  1. Fator R = folha / faturamento                   │
│  2. Regime:                                         │
│     ├─ Fator R ≥ 28% → Simples Anexo III (6%→~11%)  │
│     ├─ Fator R < 28% → Simples Anexo IV (15,5%→~19%)│
│     └─ Lucro Presumido → ~17,5% + INSS patronal     │
│  3. Carga tributária total (%)                       │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│          FÓRMULA DO PREÇO MÍNIMO                     │
│  Preço Mínimo = Custo Direto ÷                       │
│                 (1 − Carga Tributária − Margem)      │
└─────────────────────────────────────────────────────┘
```

**Exemplo:** Custo direto R$ 10.000 · Carga 10% (Simples Anexo III) · Margem 15%

```
Preço Mínimo = 10.000 ÷ (1 − 0,10 − 0,15) = 10.000 ÷ 0,75 = R$ 13.333,33
```

### 📊 Tabela de referência — Serviços de TI

| Tipo de Serviço | Custo Hora Base (R$) | Preço Mínimo Hora¹ (R$) | Com Margem 15% (R$) |
|---|---|---|---|
| Suporte técnico remoto | 80 | 133 | 153 |
| Monitoramento de infraestrutura | 60 | 100 | 115 |
| Consultoria em TI (sênior) | 200 | 333 | 383 |
| Manutenção preventiva | 100 | 167 | 192 |
| Desenvolvimento de software | 250 | 417 | 479 |
| Hospedagem / cloud management | 150 | 250 | 288 |

> ¹ Considerando Simples Anexo III (~10% de carga). Em Anexo IV (~16%), o preço mínimo sobe ~8%. Valores são premissas — validar com a contabilidade.

---

## 9. Stack Recomendada & Reaproveitamento

### ⚙️ Stack técnica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Backend** | Python 3.12 + FastAPI | Maduro para integrações, APIs REST e LLMs |
| **Banco de Dados** | PostgreSQL 15+ | Robusto, JSONB nativo, full-text search |
| **Cache / Fila** | Redis | Agendamento leve (Celery/RQ) + cache |
| **Frontend** | React (Vite) ou Vue 3 | SPA moderno; dashboards |
| **LLM (futuro)** | Agnóstico (Ollama local / API) | Migrável sem mexer no core |
| **Containerização** | Docker Compose | Reprodutível dev↔prod |
| **CI/CD** | GitHub Actions | Testes e deploy automatizados |
| **Hospedagem** | Railway/Render (V1) → AWS (V3) | Escala conforme receita |

### 🔗 Reaproveitamento do repositório atual

| Arquivo existente | Como reutilizar |
|---|---|
| `scripts/crm_collector.py` | Filosofia de coleta → evoluir para `scripts/tender_collector.py` |
| `crm/pipeline.json` | Modelo de funil/status → estender para `proposals.status` |
| `crm/targets.json` | Lista de alvos → mapear para `clients` (tipo `PUBLIC`) |
| `.github/workflows/crm_collect.yml` | Padrão de agendamento → reusar para coleta de editais |
| `public/contato.php` + `public/lib/PHPMailer/` | Canal de e-mail já pronto → alertas de edital (V3) |
| `docker-compose.yml` + `docker/nginx.conf` | Adicionar serviços PostgreSQL/Redis/MinIO na implementação |

---

## 10. Roadmap de Evolução

```
╔══════════════════════════════════════════════════════════════════╗
║                        ROADMAP V1 → V4                            ║
╠══════════════════════════════════════════════════════════════════╣
║  V1 (Mês 1–2) — Fundação                                          ║
║   ● Adaptador PNCP funcional (API → PostgreSQL)                   ║
║   ● Motor de scoring LLM (interface agnóstica, schema JSON)       ║
║   ● CLI básica: danzeroum search --keywords "TI" --uf SP          ║
║   ● Schema PostgreSQL + documentação (este arquivo)               ║
║                                                                   ║
║  V2 (Mês 3–4) — Expansão + CRM                                    ║
║   ● Adaptadores Compras.gov + Compras SP + Prefeitura SP          ║
║   ● Integração/migração do CRM (crm/*.json → PostgreSQL)          ║
║   ● Módulo de Precificação (calculadora + histórico)              ║
║   ● Primeiro dashboard web (React/Vue)                            ║
║                                                                   ║
║  V3 (Mês 5–6) — Inteligência + Mobilidade                         ║
║   ● LLM local (Ollama) + cache de análises similares              ║
║   ● Módulo de Propostas (template → PDF)                          ║
║   ● Alertas por e-mail/WhatsApp/Telegram                          ║
║   ● PWA mobile + analytics (taxa de vitória, CAC)                 ║
║                                                                   ║
║  V4 (Mês 7+) — Automação Avançada                                 ║
║   ● Envio automatizado de propostas (e-CNPJ + login nos portais)  ║
║   ● Módulo financeiro (fluxo de caixa, DRE, NF)                   ║
║   ● IA preditiva (chance de vitória por edital)                   ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 11. Riscos e Mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|---|---|---|---|
| Mudança de API/HTML dos portais | Alto | Média | Adaptadores isolados; monitorar changelogs; scraping resiliente (parser + fallback regex) |
| Qualidade insuficiente do scoring | Alto | Baixa | Começar com modelo de alta qualidade → validar → depois testar local |
| Custo de LLM escalar com volume | Médio | Média | Cache de prompts similares; rate limiting; opção de LLM local na V3 |
| Capital social limitante | Médio | Alta | Aumentar capital antes de mirar contratos maiores |
| Scraping bloqueado pelos portais | Médio | Média | Respeitar robots.txt/termos; priorizar APIs oficiais; fallback manual |
| LGPD / Compliance | Baixo | Média | Dados de licitação são públicos; respeitar termos das APIs; não armazenar dado pessoal sensível |
| Integração com CRM legado | Médio | Alta | API intermediária; ETL gradual; manter `crm/*.json` como fallback |

---

## 12. Próximo Passo (V1 Funcional)

| Entrega | Descrição |
|---|---|
| **Adaptador PNCP** | Módulo Python que busca editais de TI em SP via API oficial e salva no PostgreSQL |
| **Motor de Scoring (interface)** | Endpoint `/score` que recebe um `tender_id`, chama o LLM via provider agnóstico e grava em `tender_scores` |
| **CLI básica** | `python -m danzeroum search --keywords "tecnologia,ti" --uf SP` retornando JSON |
| **Schema PostgreSQL** | `sql/schema.sql` com as tabelas deste blueprint |
| **Documentação de setup** | `docs/setup.md` com pré-requisitos (PostgreSQL, Redis, chaves de API) e passo a passo |

---

## Referências

- Portal Nacional de Contratações Públicas (PNCP) — editais e atas: <https://pncp.gov.br/app/editais>
- Documentação/manuais de integração do PNCP (confirmar endpoints antes de implementar): <https://www.gov.br/pncp/pt-br>
- Compras.gov.br (Governo Federal): <https://www.gov.br/compras/pt-br>
- Compras SP (Governo do Estado de SP / BEC): <https://www.bec.sp.gov.br>
- JSON Schema (draft-07): <http://json-schema.org/draft-07/schema>

> Premissas tributárias e de mercado citadas neste documento devem ser validadas com a contabilidade da empresa antes de decisões financeiras.
