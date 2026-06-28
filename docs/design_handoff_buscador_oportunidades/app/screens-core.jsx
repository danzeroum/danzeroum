/* Danzeroum — telas núcleo: Dashboard, Lista, Detalhe + Scoring */

const recoTone = { GO: 'go', REVIEW: 'review', SKIP: 'skip' };

function DeadlinePill({ date }) {
  const d = window.DZ.daysTo(date);
  if (d == null) return <span className="mono" style={{ color: 'var(--faint)' }}>—</span>;
  const tone = d < 0 ? 'var(--danger)' : d <= 3 ? 'var(--review)' : 'var(--muted)';
  const txt = d < 0 ? `vencido` : d === 0 ? 'hoje' : `${d}d`;
  return (
    <span className="mono" style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: tone, fontSize: '.8rem', whiteSpace: 'nowrap' }}>
      <Icons.clock size={13} /> {window.DZ.fmtDate(date)} · {txt}
    </span>
  );
}

function FitBar({ v }) {
  const tone = v >= 0.8 ? 'var(--go)' : v >= 0.65 ? 'var(--review)' : 'var(--skip)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 9, minWidth: 92 }}>
      <div className="bar" style={{ flex: 1 }}><span style={{ width: (v * 100) + '%', background: tone }}></span></div>
      <span className="tnum" style={{ fontSize: '.8rem', color: 'var(--ink)', fontWeight: 600 }}>{v.toFixed(2)}</span>
    </div>
  );
}

const SourceTag = ({ s }) => <span className="mono" style={{ fontSize: '.68rem', color: 'var(--muted)', background: 'var(--bg-2)', border: '1px solid var(--line)', padding: '2px 7px', borderRadius: 6 }}>{s}</span>;

/* ---------------- DASHBOARD ---------------- */
function ScreenDashboard({ ctx }) {
  const T = window.DZ.tenders;
  const active = T.filter(t => t.status !== 'descartado');
  const go = active.filter(t => t.recommendation === 'GO');
  const review = active.filter(t => t.recommendation === 'REVIEW');
  const skip = active.filter(t => t.recommendation === 'SKIP');
  const pipeline = go.concat(review).reduce((s, t) => s + t.budget, 0);
  const top = [...active].sort((a, b) => b.fit - a.fit).slice(0, 5);
  const upcoming = [...active].filter(t => window.DZ.daysTo(t.deadline) >= 0).sort((a, b) => window.DZ.daysTo(a.deadline) - window.DZ.daysTo(b.deadline)).slice(0, 4);
  const total = active.length, max = Math.max(go.length, review.length, skip.length);

  const kpis = [
    { label: 'Oportunidades ativas', value: total, sub: '4 fontes monitoradas', icon: 'target', tone: 'accent' },
    { label: 'Recomendadas (GO)', value: go.length, sub: window.DZ.fmtBRLk(go.reduce((s,t)=>s+t.budget,0)) + ' em jogo', icon: 'check', tone: 'go' },
    { label: 'A revisar', value: review.length, sub: 'requerem decisão', icon: 'alert', tone: 'review' },
    { label: 'Pipeline potencial', value: window.DZ.fmtBRLk(pipeline), sub: 'GO + Revisar', icon: 'trend', tone: 'accent', big: true },
  ];

  return (
    <div>
      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 18 }}>
        {kpis.map((k, i) => {
          const Icon = Icons[k.icon];
          const tv = { accent: 'var(--accent)', go: 'var(--go)', review: 'var(--review)' }[k.tone];
          return (
            <div key={i} className="card fade-up" style={{ padding: '16px 17px', animationDelay: (i * 50) + 'ms' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span className="field-label">{k.label}</span>
                <span style={{ color: tv, opacity: .9 }}><Icon size={17} /></span>
              </div>
              <div style={{ fontSize: k.big ? '1.7rem' : '2rem', fontWeight: 600, letterSpacing: '-.02em', color: 'var(--ink)', marginTop: 8, fontFamily: k.big ? 'var(--font-mono)' : 'inherit' }}>{k.value}</div>
              <div style={{ fontSize: '.78rem', color: 'var(--muted)', marginTop: 2 }}>{k.sub}</div>
            </div>
          );
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.7fr 1fr', gap: 14 }}>
        {/* Top oportunidades */}
        <div className="card fade-up" style={{ animationDelay: '120ms', overflow: 'hidden' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '15px 18px 12px' }}>
            <div className="h-sec">Top oportunidades por aderência</div>
            <button className="btn btn-ghost btn-sm" onClick={() => ctx.go('list')}>Ver todas <Icons.chevR size={14} /></button>
          </div>
          <table className="tbl">
            <thead><tr><th>Edital</th><th>Órgão</th><th style={{ width: 130 }}>Fit</th><th>Prazo</th><th style={{ width: 88 }}></th></tr></thead>
            <tbody>
              {top.map(t => (
                <tr key={t.id} onClick={() => ctx.go('detail', t)}>
                  <td style={{ maxWidth: 280 }}>
                    <div style={{ fontWeight: 600, color: 'var(--ink)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.title}</div>
                    <div className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)', marginTop: 2 }}>{t.number} · {window.DZ.fmtBRLk(t.budget)}</div>
                  </td>
                  <td><div style={{ fontSize: '.82rem' }}>{t.org}</div><div className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)' }}>{t.uf}</div></td>
                  <td><FitBar v={t.fit} /></td>
                  <td><DeadlinePill date={t.deadline} /></td>
                  <td><Reco r={t.recommendation} sm /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="card fade-up" style={{ animationDelay: '160ms', padding: '15px 18px' }}>
            <div className="h-sec" style={{ marginBottom: 14 }}>Por recomendação</div>
            {[['GO', go.length, 'var(--go)'], ['REVIEW', review.length, 'var(--review)'], ['SKIP', skip.length, 'var(--skip)']].map(([l, n, c]) => (
              <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 11, marginBottom: 11 }}>
                <span className="mono" style={{ width: 58, fontSize: '.72rem', color: 'var(--muted)' }}>{l}</span>
                <div className="bar" style={{ flex: 1, height: 9 }}><span style={{ width: (n / max * 100) + '%', background: c, transition: 'width .6s var(--ease)' }}></span></div>
                <span className="tnum" style={{ width: 18, textAlign: 'right', fontWeight: 600, color: 'var(--ink)' }}>{n}</span>
              </div>
            ))}
            <div style={{ borderTop: '1px solid var(--line)', marginTop: 6, paddingTop: 11, display: 'flex', justifyContent: 'space-between', fontSize: '.8rem' }}>
              <span style={{ color: 'var(--muted)' }}>Taxa de aproveitamento</span>
              <span className="tnum" style={{ fontWeight: 600, color: 'var(--go)' }}>{Math.round(go.length / total * 100)}%</span>
            </div>
          </div>

          <div className="card fade-up" style={{ animationDelay: '200ms', padding: '15px 18px', flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <div className="h-sec">Prazos próximos</div>
              <span style={{ color: 'var(--review)' }}><Icons.calendar size={16} /></span>
            </div>
            {upcoming.map(t => (
              <button key={t.id} onClick={() => ctx.go('detail', t)} style={{ display: 'block', width: '100%', textAlign: 'left', padding: '9px 0', borderBottom: '1px solid var(--line)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
                  <span style={{ fontSize: '.82rem', fontWeight: 500, color: 'var(--ink)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.org}</span>
                  <DeadlinePill date={t.deadline} />
                </div>
                <div className="mono" style={{ fontSize: '.68rem', color: 'var(--faint)', marginTop: 2 }}>{t.number}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Atalhos */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14, marginTop: 14 }}>
        {[['Rodar coleta agora', 'collect', 'collect'], ['Revisar pendências', 'list', 'filter'], ['Calcular preço mínimo', 'calc', 'calc'], ['Documentos a vencer', 'docs', 'docs']].map(([l, r, ic]) => {
          const Icon = Icons[ic];
          return (
            <button key={r} className="card fade-up" onClick={() => ctx.go(r)} style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 12, textAlign: 'left', animationDelay: '240ms' }}>
              <span style={{ width: 36, height: 36, borderRadius: 9, background: 'var(--accent-wash)', color: 'var(--accent-ink)', display: 'grid', placeItems: 'center', flexShrink: 0 }}><Icon size={18} /></span>
              <span style={{ fontSize: '.86rem', fontWeight: 500, color: 'var(--ink)' }}>{l}</span>
              <span style={{ marginLeft: 'auto', color: 'var(--faint)' }}><Icons.chevR size={15} /></span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

window.ScreenDashboard = ScreenDashboard;
window.DeadlinePill = DeadlinePill;
window.FitBar = FitBar;
window.SourceTag = SourceTag;
