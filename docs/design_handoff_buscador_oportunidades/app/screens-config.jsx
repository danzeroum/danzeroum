/* Danzeroum — Configuração, Documentos & Certidões, Atestados técnicos */

function Toggle({ on }) {
  return (
    <span style={{ width: 34, height: 19, borderRadius: 20, background: on ? 'var(--accent)' : 'var(--line-2)', position: 'relative', flexShrink: 0, transition: '.2s' }}>
      <span style={{ position: 'absolute', top: 2, left: on ? 17 : 2, width: 15, height: 15, borderRadius: '50%', background: '#fff', transition: '.2s' }}></span>
    </span>
  );
}

function ScreenConfig() {
  const c = window.DZ.config;
  const [kw, setKw] = useState(c.keywords);
  const [minFit, setMinFit] = useState(c.minFit);
  const [horizon, setHorizon] = useState(c.horizon);
  const [scorer, setScorer] = useState(c.scorer);
  const [newKw, setNewKw] = useState('');

  const Section = ({ title, sub, children }) => (
    <div className="card" style={{ padding: '18px 20px' }}>
      <div style={{ marginBottom: 16 }}>
        <div className="h-sec">{title}</div>
        {sub && <div style={{ fontSize: '.82rem', color: 'var(--muted)', marginTop: 3 }}>{sub}</div>}
      </div>
      {children}
    </div>
  );

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, alignItems: 'start' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Section title="Fontes e abrangência" sub="De onde e onde buscar editais.">
          <div style={{ marginBottom: 16 }}>
            <div className="field-label" style={{ marginBottom: 8 }}>UFs monitoradas</div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {['SC', 'SP', 'PR', 'RS', 'DF', 'RJ', 'MG', 'BA'].map(u => (
                <span key={u} className={'chip chip-btn' + (c.ufs.includes(u) ? ' on' : '')}>{u}</span>
              ))}
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <div className="field-label" style={{ marginBottom: 8 }}>Modalidades</div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {['Pregão Eletrônico', 'Dispensa Eletrônica', 'Concorrência', 'Credenciamento'].map(m => (
                <span key={m} className={'chip chip-btn' + (c.modalities.includes(m) ? ' on' : '')}>{m}</span>
              ))}
            </div>
          </div>
          <div>
            <div className="field-label" style={{ marginBottom: 8 }}>Horizonte de prazo · {horizon} dias</div>
            <input type="range" min="7" max="90" step="1" value={horizon} onChange={e => setHorizon(+e.target.value)} style={{ accentColor: 'var(--accent)', width: '100%' }} />
          </div>
        </Section>

        <Section title="Palavras-chave" sub="Termos usados na busca textual (FTS) do objeto.">
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
            {kw.map(k => (
              <span key={k} className="chip" style={{ background: 'var(--accent-wash)', borderColor: 'var(--accent)', color: 'var(--accent-ink)' }}>
                {k}<button onClick={() => setKw(kw.filter(x => x !== k))} style={{ display: 'grid', placeItems: 'center', color: 'inherit', opacity: .7 }}><Icons.x size={12} /></button>
              </span>
            ))}
          </div>
          <form style={{ display: 'flex', gap: 8 }} onSubmit={e => { e.preventDefault(); if (newKw.trim()) { setKw([...kw, newKw.trim()]); setNewKw(''); } }}>
            <input className="input" placeholder="Adicionar termo…" value={newKw} onChange={e => setNewKw(e.target.value)} />
            <button className="btn" type="submit"><Icons.plus size={15} /></button>
          </form>
        </Section>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Section title="Pontuação (scoring)" sub="Como os editais são avaliados e o limiar de alerta.">
          <div style={{ marginBottom: 18 }}>
            <div className="field-label" style={{ marginBottom: 8 }}>Motor de scoring</div>
            <div style={{ display: 'flex', gap: 8 }}>
              {[['heuristico', 'Heurístico', 'pesos por regra'], ['llm', 'LLM (futuro)', 'análise por IA']].map(([v, l, d]) => (
                <button key={v} onClick={() => setScorer(v)} style={{ flex: 1, textAlign: 'left', padding: '12px 14px', borderRadius: 10, border: `1px solid ${scorer === v ? 'var(--accent)' : 'var(--line-2)'}`, background: scorer === v ? 'var(--accent-wash)' : 'var(--surface)', opacity: v === 'llm' ? .7 : 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '.88rem', fontWeight: 600, color: 'var(--ink)' }}>{l}</span>
                    <span style={{ width: 15, height: 15, borderRadius: '50%', border: `2px solid ${scorer === v ? 'var(--accent)' : 'var(--line-2)'}`, display: 'grid', placeItems: 'center' }}>{scorer === v && <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--accent)' }}></span>}</span>
                  </div>
                  <div className="mono" style={{ fontSize: '.68rem', color: 'var(--faint)', marginTop: 3 }}>{d}</div>
                </button>
              ))}
            </div>
          </div>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span className="field-label">Fit mínimo p/ alerta (min_fit)</span>
              <span className="mono" style={{ fontSize: '.8rem', fontWeight: 600, color: 'var(--accent-ink)' }}>{minFit.toFixed(2)}</span>
            </div>
            <input type="range" min="0" max="0.95" step="0.05" value={minFit} onChange={e => setMinFit(+e.target.value)} style={{ accentColor: 'var(--accent)', width: '100%' }} />
            <div className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)', marginTop: 6 }}>Editais com fit ≥ {minFit.toFixed(2)} geram alerta automático.</div>
          </div>
        </Section>

        <Section title="Agendamento" sub="Frequência da coleta automática.">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid var(--line)' }}>
            <span style={{ fontSize: '.86rem', color: 'var(--text)' }}>Coleta automática</span><Toggle on={true} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0' }}>
            <span style={{ fontSize: '.86rem', color: 'var(--text)' }}>Intervalo</span>
            <select className="input" style={{ width: 'auto', padding: '6px 10px', fontSize: '.82rem' }} defaultValue="diario">
              <option value="diario">Diário · 06:00</option><option value="12h">A cada 12h</option><option value="6h">A cada 6h</option>
            </select>
          </div>
        </Section>

        <Section title="Alertas por e-mail (SMTP)" sub="Notificações de oportunidades e prazos.">
          {[['Servidor SMTP', c.smtp.host], ['Remetente', c.smtp.from], ['Destinatário', c.smtp.to]].map(([k, v]) => (
            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--line)' }}>
              <span className="field-label" style={{ paddingTop: 2 }}>{k}</span><span className="mono" style={{ fontSize: '.8rem', color: 'var(--ink)' }}>{v}</span>
            </div>
          ))}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: 12 }}>
            <span style={{ fontSize: '.86rem', color: 'var(--text)' }}>Envio ativo</span><Toggle on={c.smtp.enabled} />
          </div>
        </Section>
      </div>
    </div>
  );
}

/* ---- Documentos & Certidões ---- */
function ScreenDocs() {
  const docs = window.DZ.documents;
  const statusMap = { valido: ['reco-go', 'Válido'], vencendo: ['reco-review', 'Vence em breve'], vencido: ['reco-skip', 'Vencido'] };
  const expiring = docs.filter(d => d.status !== 'valido');

  return (
    <div>
      {expiring.length > 0 && (
        <div className="card" style={{ padding: '13px 16px', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 12, borderColor: 'var(--review-line)', background: 'var(--review-wash)' }}>
          <Icons.alert size={19} style={{ color: 'var(--review)', flexShrink: 0 }} />
          <span style={{ fontSize: '.88rem', color: 'var(--ink)' }}><b>{expiring.length} certidões</b> requerem atenção — uma já vencida. Renove antes de habilitar em novos editais.</span>
          <button className="btn btn-sm" style={{ marginLeft: 'auto' }}><Icons.upload size={14} /> Renovar</button>
        </div>
      )}
      <div className="card" style={{ overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 18px', borderBottom: '1px solid var(--line)' }}>
          <div className="h-sec">Documentos de habilitação</div>
          <button className="btn btn-primary btn-sm"><Icons.upload size={14} /> Enviar documento</button>
        </div>
        <table className="tbl">
          <thead><tr><th>Documento</th><th>Tipo</th><th>Emissor</th><th>Emissão</th><th>Validade</th><th style={{ width: 130 }}>Situação</th></tr></thead>
          <tbody>
            {docs.map(d => {
              const [cls, label] = statusMap[d.status];
              const dd = window.DZ.daysTo(d.expires);
              return (
                <tr key={d.id} style={{ cursor: 'default' }}>
                  <td style={{ fontWeight: 600, color: 'var(--ink)', maxWidth: 280 }}><div style={{ display: 'flex', alignItems: 'center', gap: 9 }}><Icons.doc size={16} style={{ color: 'var(--faint)', flexShrink: 0 }} /> <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{d.name}</span></div></td>
                  <td><span className="chip" style={{ padding: '2px 8px', fontSize: '.68rem', fontFamily: 'var(--font-mono)' }}>{d.type}</span></td>
                  <td style={{ fontSize: '.82rem' }}>{d.issuer}</td>
                  <td className="mono" style={{ fontSize: '.8rem', color: 'var(--muted)' }}>{window.DZ.fmtDate(d.issued)}</td>
                  <td className="mono" style={{ fontSize: '.8rem', color: d.expires ? (dd < 0 ? 'var(--danger)' : dd <= 15 ? 'var(--review)' : 'var(--muted)') : 'var(--faint)' }}>{d.expires ? window.DZ.fmtDate(d.expires) : 'permanente'}{d.expires && dd >= 0 ? ` · ${dd}d` : ''}</td>
                  <td><span className={'reco ' + cls}><span className="dot"></span>{label}</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ---- Atestados técnicos ---- */
function ScreenCerts() {
  const certs = window.DZ.certificates;
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <div style={{ fontSize: '.86rem', color: 'var(--muted)' }}>Portfólio de contratos executados — comprova capacidade técnica na habilitação.</div>
        <button className="btn btn-primary btn-sm"><Icons.plus size={14} /> Novo atestado</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 14 }}>
        {certs.map(c => (
          <div key={c.id} className="card" style={{ padding: '18px 20px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
                <span style={{ width: 38, height: 38, borderRadius: 10, background: 'var(--accent-wash)', color: 'var(--accent-ink)', display: 'grid', placeItems: 'center', flexShrink: 0 }}><Icons.cert size={19} /></span>
                <div><div style={{ fontSize: '.96rem', fontWeight: 600, color: 'var(--ink)' }}>{c.client}</div><div className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)' }}>{c.year} · {c.volume}</div></div>
              </div>
              <span className="tnum" style={{ fontSize: '.84rem', fontWeight: 600, color: 'var(--ink)' }}>{window.DZ.fmtBRLk(c.value)}</span>
            </div>
            <p style={{ fontSize: '.86rem', color: 'var(--text)', lineHeight: 1.5, margin: '14px 0 12px' }}>{c.object}</p>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {c.tags.map(t => <span key={t} className="chip" style={{ padding: '3px 9px', fontSize: '.72rem' }}>{t}</span>)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

window.ScreenConfig = ScreenConfig;
window.ScreenDocs = ScreenDocs;
window.ScreenCerts = ScreenCerts;
