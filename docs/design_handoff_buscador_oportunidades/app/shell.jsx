/* Danzeroum — shell: sidebar, topbar, roteador, tema */
const { useState, useEffect, useMemo, useRef } = React;

const NAV = [
  { group: 'Operação', items: [
    { id: 'dashboard', label: 'Painel', icon: 'dashboard' },
    { id: 'list', label: 'Oportunidades', icon: 'target', count: () => window.DZ.tenders.filter(t => t.status !== 'descartado').length },
    { id: 'collect', label: 'Coleta', icon: 'collect' },
    { id: 'alerts', label: 'Alertas', icon: 'bell', count: () => window.DZ.alerts.filter(a => !a.read).length },
  ]},
  { group: 'Negócio', items: [
    { id: 'proposals', label: 'Propostas', icon: 'proposals' },
    { id: 'calc', label: 'Calculadora', icon: 'calc' },
    { id: 'crm', label: 'CRM / Clientes', icon: 'crm' },
    { id: 'docs', label: 'Documentos', icon: 'docs', count: () => window.DZ.documents.filter(d => d.status !== 'valido').length },
    { id: 'certs', label: 'Atestados', icon: 'cert' },
  ]},
  { group: 'Sistema', items: [
    { id: 'config', label: 'Configuração', icon: 'config' },
  ]},
];

const TITLES = {
  dashboard: ['Painel', 'Visão geral das oportunidades e do funil'],
  list: ['Oportunidades', 'Editais coletados e pontuados'],
  detail: ['Oportunidade', 'Detalhe do edital + análise'],
  collect: ['Coleta', 'Execução e fontes de dados'],
  alerts: ['Alertas', 'Notificações de oportunidades, prazos e documentos'],
  proposals: ['Propostas', 'Funil de propostas por status'],
  calc: ['Calculadora de preço mínimo', 'Fator R · Simples Nacional'],
  crm: ['CRM / Clientes', 'Relacionamento e funil comercial'],
  docs: ['Documentos & Certidões', 'Habilitação e validade'],
  certs: ['Atestados técnicos', 'Portfólio para habilitação'],
  config: ['Configuração', 'Fontes, filtros e alertas'],
};

function useTheme() {
  const [theme, setTheme] = useState(() => localStorage.getItem('dz-theme') || 'light');
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('dz-theme', theme);
  }, [theme]);
  return [theme, setTheme];
}

function Sidebar({ route, go }) {
  return (
    <aside className="sidebar">
      <div className="sb-brand">
        <Logo size={30} dark={document.documentElement.classList.contains('dark')} />
        <span className="sb-word">dan<span className="z">zero</span>um</span>
      </div>
      <nav className="sb-nav scroll">
        {NAV.map(grp => (
          <div key={grp.group}>
            <div className="sb-group-label eyebrow">{grp.group}</div>
            {grp.items.map(it => {
              const Icon = Icons[it.icon];
              const active = route === it.id || (route === 'detail' && it.id === 'list');
              const cnt = it.count ? it.count() : null;
              return (
                <button key={it.id} className={'nav-item' + (active ? ' active' : '')} onClick={() => go(it.id)}>
                  <Icon /> {it.label}
                  {cnt ? <span className="count">{cnt}</span> : null}
                </button>
              );
            })}
          </div>
        ))}
      </nav>
      <div className="sb-foot">
        <div className="nav-item" style={{ cursor: 'default', gap: 10 }}>
          <div style={{ width: 30, height: 30, borderRadius: 8, background: 'var(--navy)', display: 'grid', placeItems: 'center', color: '#fff', fontWeight: 600, fontSize: '.78rem', flexShrink: 0 }}>DL</div>
          <div style={{ lineHeight: 1.2 }}>
            <div style={{ fontSize: '.84rem', fontWeight: 600, color: 'var(--ink)' }}>Daniel Lau</div>
            <div className="mono" style={{ fontSize: '.66rem', color: 'var(--faint)' }}>Danzeroum · admin</div>
          </div>
        </div>
      </div>
    </aside>
  );
}

function Topbar({ route, theme, setTheme, go, query, setQuery }) {
  const [t1, t2] = TITLES[route] || ['', ''];
  const unread = window.DZ.alerts.filter(a => !a.read).length;
  return (
    <header className="topbar">
      <div style={{ minWidth: 0 }}>
        <div className="h-page" style={{ fontSize: '1.12rem', lineHeight: 1.1 }}>{t1}</div>
      </div>
      <div style={{ flex: 1 }}></div>
      <div style={{ position: 'relative', width: 'min(340px, 32vw)' }}>
        <span style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', color: 'var(--faint)', pointerEvents: 'none' }}><Icons.search size={16} /></span>
        <input className="input" style={{ paddingLeft: 34 }} placeholder="Buscar editais, órgãos, objetos…"
          value={query} onChange={e => { setQuery(e.target.value); if (route !== 'list') go('list'); }} />
      </div>
      <button className="icon-btn" onClick={() => go('alerts')} style={{ position: 'relative' }} title="Alertas">
        <Icons.bell />
        {unread ? <span style={{ position: 'absolute', top: 7, right: 7, width: 8, height: 8, borderRadius: '50%', background: 'var(--brand)', border: '2px solid var(--surface)' }}></span> : null}
      </button>
      <button className="icon-btn" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} title="Tema">
        {theme === 'dark' ? <Icons.sun /> : <Icons.moon />}
      </button>
      <button className="btn btn-primary btn-sm" onClick={() => go('collect')}><Icons.collect size={15} /> Coletar</button>
    </header>
  );
}

function App() {
  const [theme, setTheme] = useTheme();
  const [route, setRoute] = useState('dashboard');
  const [selected, setSelected] = useState(null);
  const [query, setQuery] = useState('');
  const [listFilter, setListFilter] = useState(null);
  const contentRef = useRef(null);

  const go = (r, payload) => {
    if (r === 'detail') setSelected(payload);
    if (r === 'list' && payload) setListFilter(payload);
    setRoute(r);
    if (contentRef.current) contentRef.current.scrollTop = 0;
  };

  const ctx = { go, query, setQuery, selected, setSelected, listFilter, setListFilter, theme };

  const Screen = {
    dashboard: ScreenDashboard, list: ScreenList, detail: ScreenDetail,
    collect: ScreenCollect, alerts: ScreenAlerts, proposals: ScreenProposals,
    calc: ScreenCalc, crm: ScreenCRM, docs: ScreenDocs, certs: ScreenCerts,
    config: ScreenConfig,
  }[route] || ScreenDashboard;

  return (
    <div className="app">
      <Sidebar route={route} go={go} />
      <div className="main">
        <Topbar route={route} theme={theme} setTheme={setTheme} go={go} query={query} setQuery={setQuery} />
        <div className="content scroll" ref={contentRef}>
          <div className="page fade-in" key={route + (selected?.id || '')}>
            <Screen ctx={ctx} />
          </div>
        </div>
      </div>
    </div>
  );
}

window.DZApp = App;
