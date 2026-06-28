/* ============================================================
   Danzeroum — dados de exemplo (BR). Editais plausíveis de TI/serviços.
   Espelha os contratos de tracker/sql/schema.sql + scoring/schema.py.
   ============================================================ */
window.DZ = (function () {

  // tenders.* (schema.sql) + score (SCORE_SCHEMA)
  const tenders = [
    {
      id: 'PNCP-2026-000412', source: 'PNCP', org: 'Tribunal de Justiça do Paraná',
      uf: 'PR', city: 'Curitiba', category: 'TI / Software',
      modality: 'Pregão Eletrônico', number: 'PE 041/2026',
      title: 'Solução de gestão documental e assinatura eletrônica para o 1º grau',
      budget: 2480000, deadline: '2026-07-14', published: '2026-06-22', status: 'novo',
      fit: 0.91, risk: 0.22, complexity: 0.48, recommendation: 'GO',
      pricing: 'R$ 1,98M – R$ 2,30M (margem ~22% no teto)',
      analysis: 'Forte aderência ao portfólio de gestão documental da Danzeroum. Objeto descreve fluxo de protocolo, GED e assinatura ICP-Brasil — todos cobertos pelo BuildToValue Governance. Risco baixo: exigência de atestado de 50% do quantitativo já é coberta pelo contrato do TJ-SC. Prazo confortável (22 dias).',
      requirements: [
        { t: 'Atestado de capacidade técnica ≥ 50% do volume', ok: true },
        { t: 'Certidão de regularidade fiscal federal (CND)', ok: true },
        { t: 'Integração com ICP-Brasil / assinatura digital', ok: true },
        { t: 'SLA de disponibilidade 99,5% com data center nacional', ok: false },
        { t: 'Capital social mínimo R$ 248.000', ok: true },
      ],
      raw: { numeroControlePNCP: '00418-9-000412/2026', modalidadeNome: 'Pregão - Eletrônico', amparoLegal: 'Lei 14.133/2021, Art. 28, I', orgaoEntidade: { razaoSocial: 'TJPR', cnpj: '77.821.841/0001-94' }, valorTotalEstimado: 2480000.00, situacaoCompraNome: 'Divulgada no PNCP' },
    },
    {
      id: 'CN-2026-90218', source: 'ComprasNet', org: 'Ministério da Gestão e Inovação',
      uf: 'DF', city: 'Brasília', category: 'TI / Software',
      modality: 'Pregão Eletrônico', number: 'PE 218/2026',
      title: 'Plataforma de inteligência jurídica com IA generativa para análise de processos',
      budget: 5900000, deadline: '2026-07-09', published: '2026-06-19', status: 'novo',
      fit: 0.84, risk: 0.41, complexity: 0.72, recommendation: 'REVIEW',
      pricing: 'R$ 4,7M – R$ 5,6M — revisar custo de inferência LLM',
      analysis: 'Aderência alta ao produto Central de Inteligência Jurídica, mas complexidade elevada: exige RAG sobre 2M+ documentos e on-premise. Margem pressionada por custo de GPU. Recomenda revisão de viabilidade técnica e parceria de infraestrutura antes de decidir.',
      requirements: [
        { t: 'Atestado de projeto de IA/NLP em órgão público', ok: true },
        { t: 'Hospedagem on-premise homologada (TR item 7.3)', ok: false },
        { t: 'Equipe com 2 cientistas de dados sênior dedicados', ok: false },
        { t: 'Certidão negativa trabalhista (CNDT)', ok: true },
        { t: 'Garantia contratual de 5% (R$ 295.000)', ok: true },
      ],
      raw: { uasg: '201056', modalidade: 'Pregão Eletrônico', criterioJulgamento: 'Menor preço por lote', valorEstimado: 5900000.00, srp: true },
    },
    {
      id: 'PNCP-2026-000377', source: 'PNCP', org: 'Prefeitura de Florianópolis',
      uf: 'SC', city: 'Florianópolis', category: 'Serviços',
      modality: 'Pregão Eletrônico', number: 'PE 377/2026',
      title: 'Serviço de conciliação contábil automatizada para a Secretaria da Fazenda',
      budget: 880000, deadline: '2026-07-02', published: '2026-06-20', status: 'em_analise',
      fit: 0.88, risk: 0.18, complexity: 0.35, recommendation: 'GO',
      pricing: 'R$ 690k – R$ 820k (margem ~28%)',
      analysis: 'Encaixe direto com o ConciliaIA. Baixíssima complexidade, objeto bem delimitado, prefeitura com histórico de pagamento em dia. Prazo curto (12 dias) é o único ponto de atenção — preparar proposta com antecedência.',
      requirements: [
        { t: 'Atestado de conciliação contábil em ente público', ok: true },
        { t: 'CRF FGTS válida', ok: true },
        { t: 'Equipe com contador responsável (CRC ativo)', ok: true },
        { t: 'Prazo de implantação ≤ 45 dias', ok: true },
      ],
      raw: { numeroControlePNCP: '82951-7-000377/2026', modalidadeNome: 'Pregão - Eletrônico', valorTotalEstimado: 880000.00, situacaoCompraNome: 'Recebendo proposta' },
    },
    {
      id: 'BEC-2026-11540', source: 'BEC-SP', org: 'SEFAZ São Paulo',
      uf: 'SP', city: 'São Paulo', category: 'TI / Software',
      modality: 'Pregão Eletrônico', number: 'PE 1154/2026',
      title: 'Licenciamento de plataforma de governança corporativa e compliance',
      budget: 3200000, deadline: '2026-07-21', published: '2026-06-24', status: 'novo',
      fit: 0.79, risk: 0.34, complexity: 0.55, recommendation: 'REVIEW',
      pricing: 'R$ 2,6M – R$ 3,0M — verificar exigência de capital',
      analysis: 'BuildToValue Governance atende o escopo funcional, mas o edital exige capital social de R$ 640k (2x o nosso) e atestado de 1.000 usuários simultâneos. Avaliar consórcio ou comprovação por soma de contratos.',
      requirements: [
        { t: 'Capital social mínimo R$ 640.000', ok: false },
        { t: 'Atestado de 1.000 usuários simultâneos', ok: false },
        { t: 'Certidão de regularidade do FGTS', ok: true },
        { t: 'ISO 27001 ou equivalente', ok: true },
      ],
      raw: { ofertaCompra: '110800000012026OC11540', modalidade: 'Pregão Eletrônico', valorReferencia: 3200000.00 },
    },
    {
      id: 'PNCP-2026-000301', source: 'PNCP', org: 'Universidade Federal de Santa Catarina',
      uf: 'SC', city: 'Florianópolis', category: 'TI / Software',
      modality: 'Dispensa Eletrônica', number: 'DE 030/2026',
      title: 'Chatbot corporativo com IA para atendimento ao estudante',
      budget: 320000, deadline: '2026-06-30', published: '2026-06-18', status: 'em_analise',
      fit: 0.86, risk: 0.15, complexity: 0.3, recommendation: 'GO',
      pricing: 'R$ 250k – R$ 300k (margem ~32%)',
      analysis: 'Dispensa eletrônica de baixo valor — encaixe perfeito para o btvChatCorp. Processo ágil, baixa concorrência esperada, ótima relação esforço/retorno e porta de entrada para a conta UFSC.',
      requirements: [
        { t: 'Atestado de chatbot/IA conversacional', ok: true },
        { t: 'CND federal e CNDT', ok: true },
        { t: 'Implantação ≤ 30 dias', ok: true },
      ],
      raw: { numeroControlePNCP: '83899-1-000301/2026', modalidadeNome: 'Dispensa - Eletrônica', valorTotalEstimado: 320000.00 },
    },
    {
      id: 'CN-2026-90455', source: 'ComprasNet', org: 'Banco Central do Brasil',
      uf: 'DF', city: 'Brasília', category: 'TI / Software',
      modality: 'Pregão Eletrônico', number: 'PE 455/2026',
      title: 'Sistema de monitoramento de operações cripto para supervisão',
      budget: 4100000, deadline: '2026-08-05', published: '2026-06-25', status: 'novo',
      fit: 0.58, risk: 0.62, complexity: 0.81, recommendation: 'SKIP',
      pricing: '—',
      analysis: 'Apesar de tangenciar o CriptoTrade, o objeto é de supervisão regulatória com requisitos de segurança bancária (Resolução BCB) fora do portfólio atual. Complexidade e risco altos, aderência insuficiente. Recomenda-se não participar nesta fase.',
      requirements: [
        { t: 'Certificação de segurança bancária (CVM/BCB)', ok: false },
        { t: 'Atestado de sistema antifraude em instituição financeira', ok: false },
        { t: 'Equipe com 5+ engenheiros de segurança', ok: false },
        { t: 'Garantia de 5% (R$ 205.000)', ok: true },
      ],
      raw: { uasg: '180001', modalidade: 'Pregão Eletrônico', valorEstimado: 4100000.00, sigiloso: false },
    },
    {
      id: 'PNCP-2026-000288', source: 'PNCP', org: 'Governo do Estado do RS',
      uf: 'RS', city: 'Porto Alegre', category: 'Serviços',
      modality: 'Pregão Eletrônico', number: 'PE 288/2026',
      title: 'Agente autônomo de execução de tarefas administrativas (RPA + IA)',
      budget: 1450000, deadline: '2026-07-18', published: '2026-06-23', status: 'novo',
      fit: 0.82, risk: 0.29, complexity: 0.5, recommendation: 'GO',
      pricing: 'R$ 1,15M – R$ 1,36M (margem ~24%)',
      analysis: 'Aderente ao ExecutAgent. Escopo de automação de processos administrativos bem definido, risco moderado. Estado do RS com histórico de contratos de TI estáveis. Boa oportunidade de expansão regional no Sul.',
      requirements: [
        { t: 'Atestado de automação (RPA) em órgão público', ok: true },
        { t: 'CRF FGTS e CND', ok: true },
        { t: 'SLA de suporte 8x5 com escalonamento', ok: true },
        { t: 'Capital social R$ 145.000', ok: true },
      ],
      raw: { numeroControlePNCP: '87654-2-000288/2026', modalidadeNome: 'Pregão - Eletrônico', valorTotalEstimado: 1450000.00 },
    },
    {
      id: 'BEC-2026-11602', source: 'BEC-SP', org: 'Prefeitura de Campinas',
      uf: 'SP', city: 'Campinas', category: 'Serviços',
      modality: 'Pregão Eletrônico', number: 'PE 1160/2026',
      title: 'Manutenção evolutiva de portal de transparência municipal',
      budget: 540000, deadline: '2026-07-11', published: '2026-06-21', status: 'descartado',
      fit: 0.49, risk: 0.4, complexity: 0.44, recommendation: 'SKIP',
      pricing: '—',
      analysis: 'Objeto de manutenção de sistema legado em tecnologia que não dominamos (PHP/Drupal antigo). Margem baixa e escopo de sustentação que desvia do foco de produto. Descartado.',
      requirements: [
        { t: 'Atestado em manutenção de portal de transparência', ok: false },
        { t: 'Equipe com desenvolvedor Drupal sênior', ok: false },
        { t: 'CND e CRF', ok: true },
      ],
      raw: { ofertaCompra: '110800000012026OC11602', valorReferencia: 540000.00 },
    },
  ];

  // documents.* — certidões e validade
  const documents = [
    { id: 'd1', type: 'CND', name: 'Certidão Negativa de Débitos Federais', issuer: 'Receita Federal', issued: '2026-04-02', expires: '2026-09-29', status: 'valido' },
    { id: 'd2', type: 'CRF', name: 'Certificado de Regularidade do FGTS', issuer: 'Caixa', issued: '2026-06-01', expires: '2026-06-30', status: 'vencendo' },
    { id: 'd3', type: 'CNDT', name: 'Certidão Negativa de Débitos Trabalhistas', issuer: 'TST', issued: '2026-05-12', expires: '2026-11-08', status: 'valido' },
    { id: 'd4', type: 'FISCAL', name: 'Certidão de Regularidade Fiscal Municipal — Fpolis', issuer: 'Pref. Florianópolis', issued: '2026-03-20', expires: '2026-06-18', status: 'vencido' },
    { id: 'd5', type: 'ATESTADO', name: 'Atestado de Capacidade Técnica — TJ-SC (GED)', issuer: 'TJ-SC', issued: '2025-11-10', expires: null, status: 'valido' },
    { id: 'd6', type: 'FALENCIA', name: 'Certidão Negativa de Falência e Concordata', issuer: 'TJ-SC', issued: '2026-05-28', expires: '2026-08-26', status: 'valido' },
    { id: 'd7', type: 'CONTRATO', name: 'Contrato Social Consolidado', issuer: 'JUCESC', issued: '2024-02-15', expires: null, status: 'valido' },
  ];

  // proposals.* — kanban por status
  const proposals = [
    { id: 'p1', tender: 'PNCP-2026-000377', title: 'Conciliação contábil — Pref. Florianópolis', value: 760000, version: 'v2', validity: '2026-08-01', status: 'SENT', owner: 'Daniel' },
    { id: 'p2', tender: 'PNCP-2026-000301', title: 'Chatbot estudante — UFSC', value: 278000, version: 'v1', validity: '2026-07-30', status: 'UNDER_REVIEW', owner: 'Daniel' },
    { id: 'p3', tender: 'PNCP-2026-000412', title: 'Gestão documental — TJPR', value: 2150000, version: 'v1', validity: '2026-08-14', status: 'DRAFT', owner: 'Daniel' },
    { id: 'p4', tender: 'PNCP-2025-000910', title: 'Governança — Pref. Joinville', value: 1320000, version: 'v3', validity: '2026-05-20', status: 'WIN', owner: 'Daniel' },
    { id: 'p5', tender: 'CN-2025-88120', title: 'IA jurídica — TRF4', value: 3400000, version: 'v2', validity: '2026-04-10', status: 'LOST', owner: 'Daniel' },
    { id: 'p6', tender: 'BEC-2025-10330', title: 'Portal transparência — Pref. Santos', value: 480000, version: 'v1', validity: '2026-03-30', status: 'DISQUALIFIED', owner: 'Daniel' },
    { id: 'p7', tender: 'PNCP-2026-000288', title: 'Agente RPA — Governo RS', value: 1280000, version: 'v1', validity: '2026-08-18', status: 'DRAFT', owner: 'Daniel' },
  ];

  // technical_certificates.*
  const certificates = [
    { id: 'c1', client: 'Tribunal de Justiça de SC', object: 'Gestão eletrônica de documentos (GED) e protocolo', value: 1900000, year: 2025, volume: '1.2M docs/ano', tags: ['GED', 'Assinatura digital'] },
    { id: 'c2', client: 'Prefeitura de Joinville', object: 'Plataforma de governança e compliance', value: 1320000, year: 2025, volume: '800 usuários', tags: ['Governança', 'ISO 27001'] },
    { id: 'c3', client: 'TRF4', object: 'Análise documental assistida por IA (piloto)', value: 540000, year: 2024, volume: '350k processos', tags: ['IA', 'NLP'] },
    { id: 'c4', client: 'SEFAZ-SC', object: 'Conciliação contábil automatizada', value: 690000, year: 2024, volume: '24 entes', tags: ['Conciliação', 'Contábil'] },
  ];

  // clients.* + crm pipeline
  const clients = [
    { id: 'cl1', name: 'Tribunal de Justiça do Paraná', uf: 'PR', stage: 'oportunidade', value: 2480000, lastContact: '2026-06-24', contact: 'Dir. de TI — Marcos R.', tenders: 1 },
    { id: 'cl2', name: 'UFSC', uf: 'SC', stage: 'proposta', value: 278000, lastContact: '2026-06-26', contact: 'Setic — Ana P.', tenders: 1 },
    { id: 'cl3', name: 'Prefeitura de Florianópolis', uf: 'SC', stage: 'proposta', value: 760000, lastContact: '2026-06-25', contact: 'Sec. Fazenda — João L.', tenders: 2 },
    { id: 'cl4', name: 'Governo do Estado do RS', uf: 'RS', stage: 'qualificacao', value: 1450000, lastContact: '2026-06-23', contact: 'PROCERGS — Carla M.', tenders: 1 },
    { id: 'cl5', name: 'Tribunal de Justiça de SC', uf: 'SC', stage: 'cliente', value: 1900000, lastContact: '2026-06-15', contact: 'DTI — Roberto S.', tenders: 3 },
    { id: 'cl6', name: 'Ministério da Gestão', uf: 'DF', stage: 'qualificacao', value: 5900000, lastContact: '2026-06-19', contact: 'SGD — Felipe A.', tenders: 1 },
  ];

  // alerts / notifications (min_fit + expirações)
  const alerts = [
    { id: 'a1', kind: 'oportunidade', level: 'go', time: 'há 2h', title: 'Nova oportunidade GO — fit 0,91', body: 'PE 041/2026 · TJPR · Gestão documental · R$ 2,48M', ref: 'PNCP-2026-000412', read: false },
    { id: 'a2', kind: 'prazo', level: 'review', time: 'há 5h', title: 'Prazo se encerrando em 2 dias', body: 'DE 030/2026 · UFSC · Chatbot estudante — proposta ainda em revisão', ref: 'PNCP-2026-000301', read: false },
    { id: 'a3', kind: 'documento', level: 'danger', time: 'ontem', title: 'Certidão vencida', body: 'Certidão Fiscal Municipal (Fpolis) venceu em 18/06 — renovar antes do PE 377', ref: 'd4', read: false },
    { id: 'a4', kind: 'documento', level: 'review', time: 'ontem', title: 'CRF FGTS vence em 2 dias', body: 'Certificado de Regularidade do FGTS expira em 30/06', ref: 'd2', read: true },
    { id: 'a5', kind: 'oportunidade', level: 'go', time: 'há 1 dia', title: 'Nova oportunidade GO — fit 0,88', body: 'PE 377/2026 · Pref. Florianópolis · Conciliação contábil · R$ 880k', ref: 'PNCP-2026-000377', read: true },
    { id: 'a6', kind: 'coleta', level: 'skip', time: 'há 1 dia', title: 'Coleta concluída — 14 novos editais', body: '4 fontes varridas · 14 novos · 3 GO · 1 erro (BEC-SP timeout)', ref: null, read: true },
  ];

  // collection sources / runs
  const sources = [
    { id: 'pncp', name: 'PNCP', label: 'Portal Nacional de Contratações Públicas', enabled: true, last: 'há 2h', collected: 142, new: 8, errors: 0 },
    { id: 'comprasnet', name: 'ComprasNet', label: 'Compras.gov.br (Governo Federal)', enabled: true, last: 'há 2h', collected: 96, new: 4, errors: 0 },
    { id: 'bec', name: 'BEC-SP', label: 'Bolsa Eletrônica de Compras — SP', enabled: true, last: 'há 2h', collected: 51, new: 2, errors: 1 },
    { id: 'licitacoes-e', name: 'Licitações-e', label: 'Banco do Brasil', enabled: false, last: 'há 3 dias', collected: 0, new: 0, errors: 0 },
  ];

  const runs = [
    { id: 'r1', at: '28/06 06:00', trigger: 'agendado', collected: 289, fresh: 14, scored: 14, alerts: 3, errors: 1, secs: 47 },
    { id: 'r2', at: '27/06 06:00', trigger: 'agendado', collected: 276, fresh: 9, scored: 9, alerts: 2, errors: 0, secs: 41 },
    { id: 'r3', at: '26/06 18:12', trigger: 'manual', collected: 281, fresh: 3, scored: 3, alerts: 1, errors: 0, secs: 39 },
    { id: 'r4', at: '26/06 06:00', trigger: 'agendado', collected: 273, fresh: 11, scored: 11, alerts: 4, errors: 2, secs: 52 },
  ];

  const config = {
    ufs: ['SC', 'SP', 'PR', 'RS', 'DF'],
    keywords: ['gestão documental', 'inteligência jurídica', 'chatbot', 'conciliação contábil', 'governança', 'RPA', 'IA generativa', 'assinatura digital'],
    modalities: ['Pregão Eletrônico', 'Dispensa Eletrônica', 'Concorrência'],
    categories: ['TI / Software', 'Serviços'],
    horizon: 45, minFit: 0.6, interval: '06:00 diário', scorer: 'heuristico',
    smtp: { host: 'smtp.danzeroum.com', from: 'alertas@danzeroum.com', to: 'dan@danzeroum.com', enabled: true },
  };

  const fmtBRL = (n) => n == null ? '—' : n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
  const fmtBRLk = (n) => {
    if (n == null) return '—';
    if (n >= 1e6) return 'R$ ' + (n / 1e6).toLocaleString('pt-BR', { maximumFractionDigits: 2 }) + 'M';
    if (n >= 1e3) return 'R$ ' + (n / 1e3).toLocaleString('pt-BR', { maximumFractionDigits: 0 }) + 'k';
    return fmtBRL(n);
  };
  const daysTo = (d) => {
    if (!d) return null;
    const ms = new Date(d + 'T00:00:00') - new Date('2026-06-28T00:00:00');
    return Math.round(ms / 86400000);
  };
  const fmtDate = (d) => d ? new Date(d + 'T00:00:00').toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }) : '—';

  return { tenders, documents, proposals, certificates, clients, alerts, sources, runs, config, fmtBRL, fmtBRLk, daysTo, fmtDate };
})();
