/* Danzeroum — Lista de oportunidades (list / list_scored) */
function ScreenList({ ctx }) {
  const all = window.DZ.tenders;
  const [reco, setReco] = useState(ctx.listFilter?.reco || 'all');
  const [uf, setUf] = useState('all');
  const [cat, setCat] = useState('all');
  const [src, setSrc] = useState('all');
  const [minFit, setMinFit] = useState(0);
  const [showDiscarded, setShowDiscarded] = useState(false);
  const [sort, setSort] = useState('fit');
  const q = (ctx.query || '').toLowerCase();

  const ufs = [...new Set(all.map(t => t.uf))];
  const cats = [...new Set(all.map(t => t.category))];
  const srcs = [...new Set(all.map(t => t.source))];

  let rows = all.filter(t => {
    if (!showDiscarded && t.status === 'descartado') return false;
    if (reco !== 'all' && t.recommendation !== reco) return false;
    if (uf !== 'all' && t.uf !== uf) return false;
    if (cat !== 'all' && t.category !== cat) return false;
    if (src !== 'all' && t.source !== src) return false;
    if (t.fit < minFit) return false;
    if (q && !(t.title + t.org + t.number + t.category).toLowerCase().includes(q)) return false;
    return true;
  });
  rows.sort((a, b) => sort === 'fit' ? b.fit - a.fit : sort === 'budget' ? b.budget - a.budget
    : sort === 'deadline' ? window.DZ.daysTo(a.deadline) - window.DZ.daysTo(b.deadline) : b.fit - a.fit);

  const Select = ({ value, onChange, opts, label }) => (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <span className="field-label">{label}</span>
      <select className="input" style={{ width: 'auto', minWidth: 110, padding: '6px 9px', fontSize: '.82rem' }} value={value} onChange={e => onChange(e.target.value)}>
        <option value="all">Todos</option>
        {opts.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  );

  return (
    <div>
      {/* Filtros */}
      <div className="card" style={{ padding: '14px 16px', marginBottom: 14 }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap' }}>
          {[['all', 'Todas'], ['GO', 'GO'], ['REVIEW', 'Revisar'], ['SKIP', 'Pular']].map(([v, l]) => (
            <button key={v} className={'chip chip-btn' + (reco === v ? ' on' : '')} onClick={() => setReco(v)}>
              {v !== 'all' && <span style={{ width: 7, height: 7, borderRadius: '50%', background: v === 'GO' ? 'var(--go)' : v === 'REVIEW' ? 'var(--review)' : 'var(--skip)' }}></span>}
              {l}
            </button>
          ))}
          <div style={{ width: 1, background: 'var(--line)', margin: '0 4px' }}></div>
          <Select value={uf} onChange={setUf} opts={ufs} label="UF" />
          <Select value={cat} onChange={setCat} opts={cats} label="Categoria" />
          <Select value={src} onChange={setSrc} opts={srcs} label="Fonte" />
          <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span className="field-label">Fit mín · {minFit.toFixed(2)}</span>
            <input type="range" min="0" max="0.95" step="0.05" value={minFit} onChange={e => setMinFit(+e.target.value)} style={{ accentColor: 'var(--accent)', width: 120, marginTop: 6 }} />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span className="field-label">Ordenar</span>
            <select className="input" style={{ width: 'auto', padding: '6px 9px', fontSize: '.82rem' }} value={sort} onChange={e => setSort(e.target.value)}>
              <option value="fit">Aderência (fit)</option>
              <option value="deadline">Prazo</option>
              <option value="budget">Valor</option>
            </select>
          </label>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="mono" style={{ fontSize: '.74rem', color: 'var(--muted)' }}>
            <b style={{ color: 'var(--ink)' }}>{rows.length}</b> de {all.length} editais · busca FTS sobre objeto + órgão
          </div>
          <label className="chip chip-btn" style={{ cursor: 'pointer' }} onClick={() => setShowDiscarded(s => !s)}>
            <span style={{ width: 14, height: 14, borderRadius: 4, border: '1.5px solid var(--line-2)', background: showDiscarded ? 'var(--accent)' : 'transparent', display: 'grid', placeItems: 'center' }}>{showDiscarded && <Icons.check size={10} fill="var(--on-brand)" />}</span>
            Mostrar descartados
          </label>
        </div>
      </div>

      {/* Tabela */}
      <div className="card" style={{ overflow: 'hidden' }}>
        <table className="tbl">
          <thead><tr>
            <th>Objeto do edital</th><th>Órgão · UF</th><th>Fonte</th>
            <th style={{ width: 120, textAlign: 'right' }}>Valor est.</th>
            <th style={{ width: 130 }}>Fit</th><th>Prazo</th><th style={{ width: 92 }}>Status</th>
          </tr></thead>
          <tbody>
            {rows.map(t => (
              <tr key={t.id} onClick={() => ctx.go('detail', t)} style={t.status === 'descartado' ? { opacity: .55 } : null}>
                <td style={{ maxWidth: 320 }}>
                  <div style={{ fontWeight: 600, color: 'var(--ink)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.title}</div>
                  <div className="mono" style={{ fontSize: '.68rem', color: 'var(--faint)', marginTop: 2 }}>{t.number} · {t.modality} · {t.category}</div>
                </td>
                <td><div style={{ fontSize: '.82rem', maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.org}</div><div className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)' }}>{t.city} · {t.uf}</div></td>
                <td><SourceTag s={t.source} /></td>
                <td className="tnum" style={{ textAlign: 'right', fontWeight: 600, color: 'var(--ink)' }}>{window.DZ.fmtBRLk(t.budget)}</td>
                <td><FitBar v={t.fit} /></td>
                <td><DeadlinePill date={t.deadline} /></td>
                <td><Reco r={t.recommendation} sm /></td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr style={{ cursor: 'default' }}><td colSpan="7" style={{ textAlign: 'center', padding: 48, color: 'var(--faint)' }}>
                <Icons.search size={28} /><div style={{ marginTop: 8 }}>Nenhum edital corresponde aos filtros.</div>
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
window.ScreenList = ScreenList;
