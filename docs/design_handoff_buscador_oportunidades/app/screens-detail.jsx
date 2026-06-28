/* Danzeroum — Detalhe da oportunidade + card de Scoring (vitrine) */
function ScreenDetail({ ctx }) {
  const t = ctx.selected || window.DZ.tenders[0];
  const [rawOpen, setRawOpen] = useState(false);
  const reqMet = t.requirements.filter(r => r.ok).length;
  const tone = recoTone[t.recommendation];

  const fields = [
    ['Órgão', t.org], ['Modalidade', t.modality], ['Nº do processo', t.number],
    ['Município / UF', `${t.city} · ${t.uf}`], ['Categoria', t.category], ['Fonte', t.source],
    ['Publicado em', window.DZ.fmtDate(t.published)], ['Valor estimado', window.DZ.fmtBRL(t.budget)],
  ];

  return (
    <div>
      {/* breadcrumb / back */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <button className="btn btn-ghost btn-sm" onClick={() => ctx.go('list')}><Icons.chevR size={14} style={{ transform: 'rotate(180deg)' }} /> Oportunidades</button>
        <span className="mono" style={{ fontSize: '.72rem', color: 'var(--faint)' }}>/ {t.id}</span>
      </div>

      {/* header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 20, marginBottom: 20 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 9 }}>
            <Reco r={t.recommendation} />
            <SourceTag s={t.source} />
            <span className="mono" style={{ fontSize: '.72rem', color: 'var(--muted)' }}>{t.number} · {t.modality}</span>
          </div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, letterSpacing: '-.02em', color: 'var(--ink)', lineHeight: 1.2, maxWidth: '46ch', textWrap: 'balance' }}>{t.title}</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginTop: 10, color: 'var(--muted)', fontSize: '.86rem', flexWrap: 'wrap' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><Icons.building size={15} /> {t.org}</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><Icons.money size={15} /> {window.DZ.fmtBRL(t.budget)}</span>
            <DeadlinePill date={t.deadline} />
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
          <button className="btn btn-sm" onClick={() => setRawOpen(true)}><Icons.layers size={15} /> raw_json</button>
          <a className="btn btn-sm" href={t.raw?.numeroControlePNCP ? 'https://pncp.gov.br' : '#'} target="_blank" rel="noopener noreferrer"><Icons.ext size={15} /> Ver no portal</a>
          <button className="btn btn-primary btn-sm" onClick={() => ctx.go('proposals')}><Icons.proposals size={15} /> Gerar proposta</button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.15fr', gap: 16, alignItems: 'start' }}>
        {/* Esquerda: campos do edital + requisitos */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card" style={{ padding: '4px 18px' }}>
            {fields.map(([k, v], i) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, padding: '11px 0', borderBottom: i < fields.length - 1 ? '1px solid var(--line)' : 'none' }}>
                <span className="field-label" style={{ paddingTop: 2 }}>{k}</span>
                <span style={{ fontSize: '.88rem', color: 'var(--ink)', fontWeight: 500, textAlign: 'right' }}>{v}</span>
              </div>
            ))}
          </div>

          <div className="card" style={{ padding: '16px 18px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <div className="h-sec">Requisitos de habilitação</div>
              <span className="mono" style={{ fontSize: '.74rem', color: reqMet === t.requirements.length ? 'var(--go)' : 'var(--review)', fontWeight: 600 }}>{reqMet}/{t.requirements.length} atendidos</span>
            </div>
            {t.requirements.map((r, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '8px 0', borderBottom: i < t.requirements.length - 1 ? '1px solid var(--line)' : 'none' }}>
                <span style={{ width: 19, height: 19, borderRadius: '50%', flexShrink: 0, marginTop: 1, display: 'grid', placeItems: 'center', background: r.ok ? 'var(--go-wash)' : 'var(--danger-wash)', color: r.ok ? 'var(--go)' : 'var(--danger)', border: `1px solid ${r.ok ? 'var(--go-line)' : 'var(--danger)'}` }}>
                  {r.ok ? <Icons.check size={12} /> : <Icons.x size={12} />}
                </span>
                <span style={{ fontSize: '.86rem', color: r.ok ? 'var(--text)' : 'var(--ink)', fontWeight: r.ok ? 400 : 500 }}>{r.t}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Direita: card de SCORE (SCORE_SCHEMA) */}
        <div className="card fade-up" style={{ overflow: 'hidden', position: 'sticky', top: 14 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: `linear-gradient(180deg, var(--${tone}-wash), transparent)` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
              <span style={{ color: `var(--${tone})` }}><Icons.spark size={18} /></span>
              <div className="h-sec">Análise de scoring</div>
            </div>
            <span className="mono" style={{ fontSize: '.66rem', color: 'var(--faint)' }}>scorer: heurístico</span>
          </div>

          {/* gauges */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, padding: '22px 18px', borderBottom: '1px solid var(--line)' }}>
            <Gauge value={t.fit} label="Aderência" tone="go" />
            <Gauge value={t.risk} label="Risco" tone="risk" />
            <Gauge value={t.complexity} label="Complexidade" tone="review" />
          </div>

          {/* recommendation banner */}
          <div style={{ padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 12, borderBottom: '1px solid var(--line)' }}>
            <div style={{ width: 44, height: 44, borderRadius: 11, flexShrink: 0, display: 'grid', placeItems: 'center', background: `var(--${tone}-wash)`, color: `var(--${tone})`, border: `1px solid var(--${tone}-line)` }}>
              {t.recommendation === 'GO' ? <Icons.check size={22} /> : t.recommendation === 'REVIEW' ? <Icons.alert size={20} /> : <Icons.x size={20} />}
            </div>
            <div>
              <div style={{ fontSize: '.7rem', textTransform: 'uppercase', letterSpacing: '.1em', color: 'var(--faint)', fontFamily: 'var(--font-mono)' }}>Recomendação</div>
              <div style={{ fontSize: '1.05rem', fontWeight: 600, color: `var(--${tone})` }}>
                {t.recommendation === 'GO' ? 'Participar — alta aderência' : t.recommendation === 'REVIEW' ? 'Revisar antes de decidir' : 'Não participar nesta fase'}
              </div>
            </div>
          </div>

          {/* analysis */}
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--line)' }}>
            <div className="field-label" style={{ marginBottom: 8 }}>analysis_text</div>
            <p style={{ fontSize: '.9rem', lineHeight: 1.65, color: 'var(--text)' }}>{t.analysis}</p>
          </div>

          {/* pricing guidance */}
          <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 12, background: 'var(--bg-2)' }}>
            <span style={{ color: 'var(--accent-ink)' }}><Icons.money size={20} /></span>
            <div>
              <div className="field-label">pricing_guidance</div>
              <div style={{ fontSize: '.92rem', fontWeight: 600, color: 'var(--ink)', marginTop: 2 }}>{t.pricing}</div>
            </div>
            <button className="btn btn-sm" style={{ marginLeft: 'auto' }} onClick={() => ctx.go('calc')}>Calcular <Icons.chevR size={13} /></button>
          </div>
        </div>
      </div>

      {/* raw_json drawer */}
      {rawOpen && (
        <>
          <div className="drawer-scrim" onClick={() => setRawOpen(false)}></div>
          <div className="drawer">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 20px', borderBottom: '1px solid var(--line)' }}>
              <div>
                <div className="field-label">tenders.raw_json</div>
                <div className="h-sec" style={{ marginTop: 2 }}>Dado bruto da fonte · {t.source}</div>
              </div>
              <button className="icon-btn" onClick={() => setRawOpen(false)}><Icons.close /></button>
            </div>
            <div className="scroll" style={{ flex: 1, padding: 20 }}>
              <pre className="mono" style={{ fontSize: '.78rem', lineHeight: 1.7, color: 'var(--text)', background: 'var(--bg-2)', border: '1px solid var(--line)', borderRadius: 10, padding: 18, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
{JSON.stringify({ id: t.id, source: t.source, ...t.raw }, null, 2)}
              </pre>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
window.ScreenDetail = ScreenDetail;
