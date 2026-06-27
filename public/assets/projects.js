/* ============================================================
   CASES — 23 projetos validados a partir dos repositórios PÚBLICOS
   em github.com/danzeroum. Descrições extraídas dos READMEs.
   Campos comerciais adicionados: `outcome` (resultado de negócio,
   PT claro) e `featured` (destaque). `demo` dirige o badge "App ao vivo".
   Nada é inventado: claims técnicos vêm dos próprios READMEs.
   ============================================================ */
var PROJECTS = [
  // ===================== GOVERNANÇA & COMPLIANCE (4) =====================
  {
    name:'BuildToValue Governance',
    cat:'governance', tag:'Governança de IA', status:'Em produção', statusCls:'s-prod', featured:true,
    outcome:'Coloca IA em produção com trilha de auditoria à prova de adulteração e bloqueio automático de violações de privacidade.',
    desc:'Middleware de governança de agentes de IA com evidência criptográfica imutável (BLAKE3 + HMAC-SHA256). Intercepta chamadas LLM em runtime, valida contra GDPR Art. 22, HIPAA, LGPD e bloqueia violações com recibo auditável. Latência < 50ms P99.',
    tech:['Rust','Python','BLAKE3','Docker'],
    demo:'https://demo.buildtovalue.cloud',
    gh:'https://github.com/danzeroum/BuildToValueGovernance'
  },
  {
    name:'BuildToValue Framework',
    cat:'governance', tag:'Governança · ISO 42001', status:'Framework v0.9', statusCls:'s-prod',
    outcome:'Estrutura a governança de IA da empresa contra normas reconhecidas (ISO 42001, EU AI Act, NIST AI RMF) — incluindo kill switch de emergência.',
    desc:'Primeiro middleware open source de governança de IA com ISO 42001:2023 (32/32 controles), EU AI Act e NIST AI RMF (70% compatível). Kill switch de emergência (NIST MANAGE-2.4), arquitetura 3-agentes (técnico/regulatório/ético) e Huwyler Threat Taxonomy para prompt injection.',
    tech:['Python','NIST AI RMF','ISO 42001','Apache 2.0'],
    gh:'https://github.com/danzeroum/buildtovalue-governance'
  },
  {
    name:'Compliance Graph RAG',
    cat:'governance', tag:'Governança Cognitiva', status:'PoC', statusCls:'s-poc',
    outcome:'Transforma regras de compliance em conhecimento consultável para que agentes de IA tomem decisões conformes e explicáveis.',
    desc:'Sistema de governança cognitiva baseado em ontologias OWL combinadas com LLMs. Modela regras de compliance como grafo de conhecimento consultável, permitindo que agentes de IA tomem decisões conformes e explicáveis.',
    tech:['Python','OWL','LLMs','RAG'],
    gh:'https://github.com/danzeroum/compliance-graph-rag'
  },
  {
    name:'The Accountability Stack',
    cat:'governance', tag:'Paper · Teoria', status:'Acadêmico', statusCls:'s-paper',
    outcome:'Pesquisa própria que embasa a abordagem da Danzeroum: por que decisões de IA precisam de prova verificável.',
    desc:'Série de 6 papers em LaTeX sobre accountability algorítmica: tipos lineares em Rust para evidência em compile-time (P1), persistência Merkle (P2), provas ZK em Noir para redaction auditável (P3), economia da opacidade (P4), código constitucional Montesquieu (P5) e protocolo de emenda (P6).',
    tech:['LaTeX','Rust','Noir','ZK Proofs'],
    gh:'https://github.com/danzeroum/silent-decisions-proof'
  },

  // ===================== LEGALTECH (4) =====================
  {
    name:'Jurídico Platform',
    cat:'legal', tag:'LegalTech · 8 produtos', status:'Plataforma', statusCls:'s-prod',
    outcome:'Automatiza rotinas jurídico-contábeis (rating, auditoria, compliance, predição tributária) numa única plataforma Docker-first.',
    desc:'Plataforma Jurídico-Contábil Docker-First com 8 produtos de IA aplicada ao direito brasileiro: LegalScore PJ (rating jurídico-financeiro), ContabilIA (auditoria automatizada), ComplianceRadar, TaxPredict (bayesiano), LicitaWatch (PNCP), DanoBot, PetiBot e ConciliaIA. Stack com Neo4j, OpenSearch, ChromaDB e Ollama.',
    tech:['Python','FastAPI','Next.js','Neo4j','ChromaDB','Docker'],
    gh:'https://github.com/danzeroum/juridico-platform'
  },
  {
    name:'Central de Inteligência Jurídica',
    cat:'legal', tag:'Multi-Agentes · Legal', status:'Beta', statusCls:'s-beta', featured:true,
    outcome:'Acelera análise jurídica com agentes especializados por tribunal, sempre com revisão humana (HITL) e trilha de auditoria das decisões.',
    desc:'Plataforma multiagente para o setor jurídico: SupervisorAgent orquestra TribunalAgents especializados (TJSP, TJMG, TJRS, TJRJ, STF), com ArchitectAgent (Chain-of-Thought), WeightedConsensusEngine, ProgressiveAutonomyManager (HITL) e DecisionLedger para auditoria. Frontend SPA React + Vite.',
    tech:['Python','FastAPI','ChromaDB','Redis','React','Prometheus'],
    demo:'https://juridico.buildtovalue.cloud',
    gh:'https://github.com/danzeroum/Central_Inteligencia_Juridica'
  },
  {
    name:'ConciliaIA',
    cat:'legal', tag:'Reconciliação · FinTech', status:'No ar', statusCls:'s-prod', featured:true,
    outcome:'Concilia vendas com adquirentes (Cielo, Rede, Stone) e detecta divergências de MDR, chargeback e atraso de liquidação automaticamente.',
    desc:'Sistema de reconciliação financeira para e-commerce e varejo: concilia vendas do lojista com relatórios de adquirentes (Cielo, Rede, Stone), detecta divergências (MDR, NSU ausente, chargeback, atraso de liquidação) e expõe API versionada + dashboard. Monólito modular em FastAPI com PostgreSQL externo.',
    tech:['Python','FastAPI','PostgreSQL','React','Docker','Alembic'],
    demo:'https://conciliaia.buildtovalue.cloud',
    gh:'https://github.com/danzeroum/ConciliaIA'
  },
  {
    name:'NotaFiscal — NFe Processor',
    cat:'legal', tag:'Fiscal · Spring Boot', status:'MVP', statusCls:'s-beta',
    outcome:'Processa lotes de NF-e em massa, valida e exporta no padrão do ERP, com integração SEFAZ via certificado A1.',
    desc:'Processador de lotes de NF-e (BuildToFlip v5): upload de ZIP com XML/PDF, validação, exportação Excel padrão ERP e integração SEFAZ via SOAP com certificado A1. OCR experimental via Tess4J, circuit breaker Resilience4j e erros RFC 7807 com traceId.',
    tech:['Java 21','Spring Boot','Maven','Tess4J','Resilience4j'],
    gh:'https://github.com/danzeroum/NotaFiscal'
  },

  // ===================== FINTECH & CRYPTO (3) =====================
  {
    name:'Criptotrade — AI Trading',
    cat:'fintech', tag:'FinTech · Trading AI', status:'Paper Trading', statusCls:'s-prod', featured:true,
    outcome:'Orquestra decisões de trading com agentes de IA em cadeia (estratégia → risco → guardrails → humano → execução) e ledger auditável.',
    desc:'Plataforma de trading automatizado de cripto com agentes de IA especializados (Strategy → Risk → Guardrails → HITL → Execution). Ciclo testado cross-process: API FastAPI + loop orquestrador compartilham estado via SQLite WAL. Ledger append-only em JSONL + event log XES para process mining. Dashboard Streamlit com console HITL.',
    tech:['Python','FastAPI','SQLite','Streamlit','LLMs'],
    demo:'https://criptotrade.buildtovalue.cloud',
    gh:'https://github.com/danzeroum/Criptotrade'
  },
  {
    name:'Financial AI Pipeline PoC',
    cat:'fintech', tag:'FinTech · Microsserviços', status:'PoC', statusCls:'s-poc',
    outcome:'Detecta fraude em tempo real com microsserviços desacoplados por Kafka, prontos para Kubernetes.',
    desc:'Pipeline financeiro com IA para detecção de fraudes em tempo real: transacao-service (valida + publica no Kafka) e ia-service (consome + classifica via IA + persiste). Java 21 / Spring Boot 3, Kubernetes manifests, GitHub Actions CI/CD e documentação completa (arquitetura, contratos de API, runbook).',
    tech:['Java 21','Spring Boot 3','Kafka','Kubernetes','Docker'],
    gh:'https://github.com/danzeroum/financial-ai-pipeline-poc'
  },
  {
    name:'Conciliação de Transações Lab',
    cat:'fintech', tag:'FinTech · Hexagonal', status:'Lab', statusCls:'s-beta',
    outcome:'Processa arquivos EDI de conciliação bancária/cartões com precisão decimal de 100% e qualidade garantida em CI.',
    desc:'Microsserviço crítico para processamento de arquivos EDI de conciliação bancária e cartões. Arquitetura Hexagonal (Ports & Adapters) com isolamento total das regras de negócio, precisão decimal 100% via BigDecimal + RoundingMode.HALF_UP, cloud-native Azure (Actuator probes, logs JSON para Azure Monitor) e CI/CD GitHub Actions com Quality Gate JaCoCo ≥ 80%.',
    tech:['Java 17','Spring Boot 3.2','JUnit 5','JaCoCo','Docker','Azure'],
    gh:'https://github.com/danzeroum/conciliacao-transacoes-lab'
  },

  // ===================== PLATAFORMAS DE IA (3) =====================
  {
    name:'btvChatCorp',
    cat:'ai-platforms', tag:'SaaS · IA Privada', status:'Em produção', statusCls:'s-prod', featured:true,
    outcome:'IA privada enterprise sobre os dados da empresa — multi-tenant, com SSO e white-label, sem vazar dado para terceiros.',
    desc:'Plataforma de IA privada enterprise: backend Rust/Axum (monorepo de crates) com RAG (Qdrant + pgvector), LLM via Ollama, multi-tenancy, SSO (OIDC/SAML/LDAP), API pública compatível com OpenAI e white-label completo por workspace. Frontend Angular 17+ com SSE streaming. Worker Rust dedicado para ingestão de documentos.',
    tech:['Rust','Axum','Angular 17','Qdrant','PostgreSQL','Docker'],
    demo:'https://chatcorp.buildtovalue.cloud',
    gh:'https://github.com/danzeroum/btvChatCorp'
  },
  {
    name:'Executagent',
    cat:'ai-platforms', tag:'Agentes · Skills', status:'MVP', statusCls:'s-beta',
    outcome:'Executa tarefas via skills de IA com roteamento de modelo por custo e validação de qualidade dos entregáveis.',
    desc:'Plataforma de execução estruturada de tarefas via AI skills: roteador semântico escolhe skill e tier de modelo (S/M/L), skill produz deliverables, pipeline de validação checa qualidade e resultados voltam com métricas honestas. Arquitetura Supabase-first (pgmq, pgvector, RBAC), skills baseadas em SKILL.md (padrão Agent Skills), observabilidade com trace_id ponta a ponta.',
    tech:['TypeScript','Supabase','pgvector','Vite','pnpm'],
    gh:'https://github.com/danzeroum/executagent'
  },
  {
    name:'WhatsApp RAG Broker',
    cat:'ai-platforms', tag:'PoC · Messaging + RAG', status:'PoC', statusCls:'s-poc',
    outcome:'Atendimento B2B no WhatsApp oficial (Meta) com respostas ancoradas nos documentos da empresa (RAG), pronto para alto volume.',
    desc:'Assistente B2B integrado à API oficial do WhatsApp (Meta Cloud API): webhook valida assinatura HMAC-SHA256, mensagem entra em fila Redis (LPUSH/BLPOP), worker consulta ChromaDB (RAG) e responde ao usuário via API da Meta. Serverless-ready, com LLM cloud (GPT-4o-mini) ou self-hosted (Ollama).',
    tech:['Python','FastAPI','Redis','ChromaDB','Docker'],
    gh:'https://github.com/danzeroum/whatsapp-rag-broker'
  },

  // ===================== CIVICTECH & DADOS (2) =====================
  {
    name:'DadoSabedoria',
    cat:'civic', tag:'CivicTech · Dados Públicos', status:'Onda 1 completa', statusCls:'s-prod',
    outcome:'Transforma dados públicos brasileiros (CAGED, BCB, IBGE) em inteligência geográfica com IA citável e privacidade por design.',
    desc:'Plataforma de inteligência de dados públicos brasileiros: ingestão real de CAGED, BCB/ESTBAN e IBGE, IVM (Índice de Vulnerabilidade Municipal) materializado, frontend Next.js com coropleta geográfica + drill-down, IA ancorada com citação (DeepSeek/Ollama), runtime de consentimento LGPD isolado com cifragem de campo e k-anonimato. Privacidade estrutural testada no CI.',
    tech:['Python','FastAPI','Next.js','PostGIS','Redis','pgvector'],
    gh:'https://github.com/danzeroum/dadosabedoria'
  },
  {
    name:'CulturaSP Adapter',
    cat:'civic', tag:'CivicTech · Open Data', status:'v1.0', statusCls:'s-prod',
    outcome:'Disponibiliza dados culturais públicos de SP via API, iCal e RSS, com scraping ético e pipeline desacoplado.',
    desc:'Adaptador open source read-only que lê dados culturais públicos de São Paulo (Sala São Paulo / OSESP), estrutura em JSON-LD / schema.org e expõe via API REST, feeds iCal e RSS. Scraping ético (robots.txt, User-Agent identificável, cache, baixa frequência). Pipeline desacoplado da API para que tráfego de API nunca vire carga no site de origem.',
    tech:['Python','FastAPI','Playwright','PostgreSQL','Redis','JSON-LD'],
    gh:'https://github.com/danzeroum/culturasp-adapter'
  },

  // ===================== EDUCAÇÃO (2) =====================
  {
    name:'EducaDigital',
    cat:'education', tag:'EdTech · EJA', status:'V1', statusCls:'s-beta',
    outcome:'Educação adaptativa offline-first para EJA, com tutor de IA, trilha personalizada e predição de risco de evasão.',
    desc:'Plataforma de educação adaptativa para EJA (3,3M de brasileiros que deixaram a escola): diagnóstico multimodal (Whisper STT + OCR + quiz), trilha adaptativa via LLM, repetição espaçada SM-2 offline, vídeo interativo com checkpoints IA, tutor virtual streaming (Claude Sonnet), gamificação com certificados PDF verificáveis e predição de risco de evasão (LightGBM). PWA offline-first para Android 7 com 2G.',
    tech:['Python 3.12','FastAPI','Next.js 14','PostgreSQL','Celery','Claude','Whisper'],
    gh:'https://github.com/danzeroum/educadigital'
  },
  {
    name:'Waldorf School System',
    cat:'education', tag:'EdTech · Gestão Escolar', status:'~75% backend', statusCls:'s-beta',
    outcome:'Gestão escolar completa (pedagogia, financeiro, comunidade) com web, mobile e conformidade LGPD.',
    desc:'Sistema completo de gestão escolar para Escolas Waldorf: pedagogia, financeiro, comunidade e conformidade LGPD. Backend Spring Boot 3 / Java 21 / MySQL 8, frontend Angular 17+ / Tailwind, mobile Flutter 3 (iOS/Android). JWT + RBAC + OpenAPI, RabbitMQ, MinIO. Infra Docker com GitHub Actions para CI/CD.',
    tech:['Java 21','Spring Boot 3','Angular 17','Flutter','MySQL','Docker'],
    gh:'https://github.com/danzeroum/waldorf-school-system'
  },

  // ===================== FERRAMENTAS & DEV (3) =====================
  {
    name:'Prompte — Prompt Engineering Pro',
    cat:'tools', tag:'Dev Tool · PWA', status:'No ar', statusCls:'s-prod', featured:true,
    outcome:'Ferramenta web offline-first para análise de domínios e geração de prompts de engenharia, instalável como PWA.',
    desc:'Ferramenta web offline-first de análise de domínios e geração de prompts de engenharia de software: 3 páginas (análise + 6 geradores avançados, 25 templates em 4 categorias, manual + playground). Design system compartilhado, i18n (pt/en), telemetria offline-first via Supabase com RLS, PWA instalável (vite-plugin-pwa), testes Jest + jsdom.',
    tech:['JavaScript','PWA','Vite','Supabase','Jest'],
    demo:'https://prompte.buildtovalue.cloud',
    gh:'https://github.com/danzeroum/prompte'
  },
  {
    name:'Gravador de Reunião',
    cat:'tools', tag:'Tool · Realtime AI', status:'Open source', statusCls:'s-prod',
    outcome:'Captura, transcreve, traduz e resume reuniões em tempo real, com diarização de falantes e LLM plugável.',
    desc:'Captura, transcreve, traduz e processa legendas da tela em tempo real: OCR multi-idioma (Tesseract), tradução local MarianMT (fallback OpenAI/DeepSeek), captura áudio WASAPI com faster-whisper + VAD silero, diarização de falantes (diart + pyannote), LLM pluggável (Ollama/OpenAI/DeepSeek), resumo automático e detecção de perguntas. GUI CustomTkinter + servidor FastAPI para Docker/VPS.',
    tech:['Python','Tesseract','Whisper','MarianMT','FastAPI','CustomTkinter'],
    gh:'https://github.com/danzeroum/gravadorlegendas'
  },
  {
    name:'Família em Equilíbrio',
    cat:'tools', tag:'Web App · Família', status:'No ar', statusCls:'s-prod',
    outcome:'App de gestão doméstica familiar com 6 módulos (rotina, casa, saúde, agenda, finanças) em Next.js + Supabase.',
    desc:'Aplicativo web de gestão doméstica familiar com 6 módulos: painel de antecipação, cadastro da família, rotina semanal, gestão da casa, saúde e medicamentos, agenda e finanças. Next.js 14 (App Router) + Tailwind + shadcn/ui, Supabase (banco + auth), Zustand para estado global e date-fns.',
    tech:['Next.js 14','Supabase','shadcn/ui','Zustand','Tailwind'],
    gh:'https://github.com/danzeroum/familia-em-equilibrio-web'
  },

  // ===================== AUTOMAÇÃO & MARTECH (2) =====================
  {
    name:'Uncover Aegis',
    cat:'automation', tag:'MarTech · NL→SQL', status:'PoC', statusCls:'s-poc',
    outcome:'Responde perguntas de marketing em linguagem natural via SQL seguro (guardrail Rust), com sanitização de PII.',
    desc:'Pipeline de insights para MarTech: linguagem natural → SQL → guardrail Rust → banco, com MMM Adstock, cache Redis, API GraphQL e deploy no Fly.io (GRU). NIFs Rust (DirtyCpu) via Rustler para validação SQL (allowlist + blocklist), sanitização de PII e cálculo de Z-Score por campanha — sem bloquear a BEAM. Phoenix LiveView + REST + GraphQL (Absinthe).',
    tech:['Elixir','Phoenix','Rust','Rustler','Redis','GraphQL'],
    gh:'https://github.com/danzeroum/uncover-aegis-nif'
  },
  {
    name:'Process Veritas — IBM BAW V3',
    cat:'automation', tag:'BPM · IBM BAW', status:'Tool', statusCls:'s-prod',
    outcome:'Documenta e analisa processos IBM BAW (incl. legados Teamworks) gerando relatórios interpretáveis por IA.',
    desc:'Sistema completo de análise e documentação de processos IBM Business Automation Workflow. Otimizado para interpretabilidade por IA: processa BPMNs modernos e legados (Teamworks), gera relatórios de qualidade para LLMs, valida estrutura BPMN, métricas executivas e saída em JSON/TXT/HTML. Arquitetura modular com DependencyExtractor, ExecutionPathGenerator e VariableEnricher.',
    tech:['Java','BPMN','IBM BAW','Maven'],
    gh:'https://github.com/danzeroum/process-veritas'
  }
];

var GH = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.92 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>';
var ARR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7M9 7h8v8"/></svg>';

function escAttr(s){ return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;'); }

// Ordem padrão: destaques primeiro, depois quem tem demo ao vivo, mantendo a ordem original como desempate.
function sortForDisplay(list){
  return list.map(function(p,i){return {p:p,i:i};}).sort(function(a,b){
    var fa=a.p.featured?1:0, fb=b.p.featured?1:0;
    if(fb-fa) return fb-fa;
    var da=a.p.demo?1:0, db=b.p.demo?1:0;
    if(db-da) return db-da;
    return a.i-b.i;
  }).map(function(o){return o.p;});
}

function matches(p, filter){
  if(filter === 'all') return true;
  if(filter === 'featured') return !!p.featured;
  return p.cat === filter;
}

function renderProjects(filter){
  var ordered = sortForDisplay(PROJECTS);
  var html = ordered.map(function(p){
    var isHidden = matches(p, filter) ? '' : ' hidden';
    var liveBadge = p.demo ? '<span class="live-badge">App ao vivo</span>' : '';
    var demoHtml = p.demo
      ? '<a class="clink demo" href="'+p.demo+'" target="_blank" rel="noopener noreferrer" aria-label="Ver app ao vivo de '+escAttr(p.name)+'">Ver app ao vivo '+ARR+'</a>'
      : '<span class="no-demo">demo em breve</span>';
    return '<article class="card'+isHidden+'" data-cat="'+p.cat+'">'
      + '<div class="ctop"><span class="tag">'+p.tag+'</span><span class="status '+p.statusCls+'">'+p.status+'</span></div>'
      + '<h3>'+p.name+'</h3>'
      + (liveBadge ? '<div style="margin-bottom:10px">'+liveBadge+'</div>' : '')
      + (p.outcome ? '<p class="outcome">'+p.outcome+'</p>' : '')
      + '<p>'+p.desc+'</p>'
      + '<div class="tech">'+p.tech.map(function(t){return '<span>'+t+'</span>';}).join('')+'</div>'
      + '<div class="clinks">'
      +   demoHtml
      +   '<a class="clink gh" href="'+p.gh+'" target="_blank" rel="noopener noreferrer" aria-label="Código de '+escAttr(p.name)+' no GitHub">'+GH+' Código</a>'
      + '</div></article>';
  }).join('');
  var grid = document.getElementById('grid');
  if(grid) grid.innerHTML = html;
  var visible = PROJECTS.filter(function(p){return matches(p, filter);}).length;
  var counter = document.getElementById('visible-count');
  if(counter) counter.textContent = visible;
}

renderProjects('featured');

// --- Filtros por categoria ---
var filterBtns = document.querySelectorAll('.fchip');
filterBtns.forEach(function(btn){
  btn.addEventListener('click', function(){
    filterBtns.forEach(function(b){
      b.classList.remove('active');
      b.setAttribute('aria-selected','false');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-selected','true');
    renderProjects(btn.dataset.filter);
  });
});
