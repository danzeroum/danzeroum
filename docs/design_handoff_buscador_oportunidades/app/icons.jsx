/* Danzeroum — ícones inline (stroke currentColor) + logo */
const Ic = ({ d, fill, size, sw = 2, children, ...p }) => (
  <svg width={size || 18} height={size || 18} viewBox="0 0 24 24" fill={fill || 'none'}
    stroke={fill ? 'none' : 'currentColor'} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" {...p}>
    {d ? <path d={d} /> : children}
  </svg>
);

const Icons = {
  dashboard: (p) => <Ic {...p}><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></Ic>,
  list: (p) => <Ic {...p}><path d="M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01"/></Ic>,
  target: (p) => <Ic {...p}><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/></Ic>,
  collect: (p) => <Ic {...p}><path d="M21 12a9 9 0 1 1-9-9c2.5 0 4.8 1 6.4 2.6"/><path d="M21 4v4h-4"/></Ic>,
  config: (p) => <Ic {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 0 1-4 0v-.1A1.6 1.6 0 0 0 7 19.4a1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 2.6 14H2.5a2 2 0 0 1 0-4h.1A1.6 1.6 0 0 0 4 7a1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.6 1.6 0 0 0 9 2.6V2.5a2 2 0 0 1 4 0v.1A1.6 1.6 0 0 0 17 4.6a1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A1.6 1.6 0 0 0 21.4 9h.1a2 2 0 0 1 0 4h-.1a1.6 1.6 0 0 0-1.1.99z"/></Ic>,
  docs: (p) => <Ic {...p}><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13l2 2 4-4"/></Ic>,
  proposals: (p) => <Ic {...p}><rect x="3" y="4" width="5" height="16" rx="1"/><rect x="9.5" y="4" width="5" height="11" rx="1"/><rect x="16" y="4" width="5" height="7" rx="1"/></Ic>,
  calc: (p) => <Ic {...p}><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01M16 15v4M8 19h4"/></Ic>,
  cert: (p) => <Ic {...p}><circle cx="12" cy="9" r="6"/><path d="M9 13.5 7.5 22l4.5-2.5L16.5 22 15 13.5"/><path d="M9.5 9l1.8 1.8L15 7"/></Ic>,
  crm: (p) => <Ic {...p}><circle cx="9" cy="8" r="3.2"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><path d="M16 7.5a3 3 0 0 1 0 5.8M18 20a5.2 5.2 0 0 0-3-4.7"/></Ic>,
  bell: (p) => <Ic {...p}><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></Ic>,
  search: (p) => <Ic {...p}><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></Ic>,
  filter: (p) => <Ic {...p}><path d="M3 5h18l-7 8v6l-4-2v-4z"/></Ic>,
  sun: (p) => <Ic {...p}><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></Ic>,
  moon: (p) => <Ic {...p}><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></Ic>,
  ext: (p) => <Ic {...p}><path d="M15 3h6v6M21 3l-9 9M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5"/></Ic>,
  close: (p) => <Ic {...p}><path d="M18 6 6 18M6 6l12 12"/></Ic>,
  chevR: (p) => <Ic {...p}><path d="m9 6 6 6-6 6"/></Ic>,
  chevD: (p) => <Ic {...p}><path d="m6 9 6 6 6-6"/></Ic>,
  arrowUp: (p) => <Ic {...p}><path d="M12 19V5M5 12l7-7 7 7"/></Ic>,
  check: (p) => <Ic {...p}><path d="M20 6 9 17l-5-5"/></Ic>,
  x: (p) => <Ic {...p}><path d="M18 6 6 18M6 6l12 12"/></Ic>,
  alert: (p) => <Ic {...p}><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></Ic>,
  clock: (p) => <Ic {...p}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></Ic>,
  calendar: (p) => <Ic {...p}><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></Ic>,
  play: (p) => <Ic {...p}><path d="M6 4l14 8-14 8z" fill="currentColor" stroke="none"/></Ic>,
  plus: (p) => <Ic {...p}><path d="M12 5v14M5 12h14"/></Ic>,
  doc: (p) => <Ic {...p}><path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/></Ic>,
  upload: (p) => <Ic {...p}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 9l5-5 5 5M12 4v12"/></Ic>,
  download: (p) => <Ic {...p}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></Ic>,
  pin: (p) => <Ic {...p}><path d="M12 21s7-6.3 7-11a7 7 0 1 0-14 0c0 4.7 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></Ic>,
  spark: (p) => <Ic {...p}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/></Ic>,
  building: (p) => <Ic {...p}><rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M9 8h.01M15 8h.01M9 12h.01M15 12h.01M9 16h.01M15 16h.01"/></Ic>,
  money: (p) => <Ic {...p}><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/></Ic>,
  trend: (p) => <Ic {...p}><path d="M3 17l6-6 4 4 8-8"/><path d="M21 7v5M21 7h-5"/></Ic>,
  layers: (p) => <Ic {...p}><path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/></Ic>,
  menu: (p) => <Ic {...p}><path d="M3 6h18M3 12h18M3 18h18"/></Ic>,
};

const Logo = ({ size = 30, dark = false }) => (
  <svg width={size} height={size * 0.78} viewBox="-10 0 80 64" aria-label="Danzeroum">
    <g fill="none" stroke={dark ? '#e8772f' : '#24324a'} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M-8 21 L1 26"/><path d="M1 26 L10 31"/><path d="M-8 43 L1 38"/><path d="M1 38 L10 33"/>
      <path d="M49 32 L60 19"/><path d="M49 32 H62"/><path d="M49 32 L60 45"/>
    </g>
    <g fill={dark ? '#e8772f' : '#24324a'}>
      <circle cx="-9" cy="20" r="2.4"/><circle cx="-9" cy="44" r="2.4"/>
      <circle cx="62" cy="18" r="2.6"/><circle cx="64" cy="32" r="2.6"/><circle cx="62" cy="46" r="2.6"/>
    </g>
    <path d="M10 11 H28 C41 11 49 20.5 49 32 C49 43.5 40 53 28 53 H10 Z" fill={dark ? '#e8772f' : '#bd4e1c'}/>
    <path d="M27 18 L37 21.6 V31 C37 38 32.5 42.4 27 45 C21.5 42.4 17 38 17 31 V21.6 Z" fill={dark ? '#fbf7f1' : '#24324a'} stroke={dark ? '#24324a' : '#fbf7f1'} strokeWidth="2.4" strokeLinejoin="round"/>
    <path d="M21.8 31 L25.2 34.4 L31 28" fill="none" stroke={dark ? '#24324a' : '#fbf7f1'} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

// Reusable bits
const Reco = ({ r, sm }) => {
  const map = { GO: ['reco-go', 'GO'], REVIEW: ['reco-review', 'Revisar'], SKIP: ['reco-skip', 'Pular'] };
  const [cls, label] = map[r] || map.SKIP;
  return <span className={'reco ' + cls} style={sm ? { fontSize: '.58rem', padding: '2px 6px' } : null}><span className="dot"></span>{label}</span>;
};

const Gauge = ({ value, label, tone = 'accent', size = 64 }) => {
  const r = 26, c = 2 * Math.PI * r, off = c * (1 - value);
  const colorVar = { go: 'var(--go)', risk: 'var(--danger)', review: 'var(--review)', accent: 'var(--accent)' }[tone] || 'var(--accent)';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 64 64" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="32" cy="32" r={r} fill="none" stroke="var(--bg-2)" strokeWidth="7"/>
          <circle cx="32" cy="32" r={r} fill="none" stroke={colorVar} strokeWidth="7" strokeLinecap="round"
            strokeDasharray={c} strokeDashoffset={off} style={{ transition: 'stroke-dashoffset .8s var(--ease)' }}/>
        </svg>
        <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '.92rem', color: 'var(--ink)' }}>
          {value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
      </div>
      <span className="field-label">{label}</span>
    </div>
  );
};

Object.assign(window, { Icons, Logo, Reco, Gauge });
