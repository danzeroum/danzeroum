/* Danzeroum — Coleta / Execução (collect / schedule) */
function ScreenCollect({ ctx }) {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logLines, setLogLines] = useState([]);
  const [done, setDone] = useState(null);
  const sources = window.DZ.sources;

  const run = () => {
    if (running) return;
    setRunning(true); setProgress(0); setDone(null); setLogLines([]);
    const steps = [
      'Iniciando pipeline.collect() …',
      'PNCP · varrendo 5 UFs, horizonte 45d …',
      'PNCP · 142 editais · 8 novos',
      'ComprasNet · varrendo UASGs monitoradas …',
      'ComprasNet · 96 editais · 4 novos',
      'BEC-SP · varrendo ofertas de compra …',
      'BEC-SP · timeout na página 3 — registrado',
      'Pontuando 14 novos editais (scorer heurístico) …',
      'Disparando 3 alertas (min_fit ≥ 0,60) …',
      'Coleta concluída.',
    ];
    let i = 0;
    const iv = setInterval(() => {
      setLogLines(l => [...l, steps[i]]);
      setProgress(Math.round(((i + 1) / steps.length) * 100));
      i++;
      if (i >= steps.length) {
        clearInterval(iv);
        setRunning(false);
        setDone({ collected: 289, fresh: 14, scored: 14, alerts: 3, errors: 1 });
      }
    }, 480);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 16, alignItems: 'start' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Run panel */}
        <div className="card" style={{ padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <div>
              <div className="h-sec">Executar coleta</div>
              <div style={{ fontSize: '.82rem', color: 'var(--muted)', marginTop: 2 }}>Varre as fontes ativas, pontua os novos editais e dispara alertas.</div>
            </div>
            <button className="btn btn-primary" onClick={run} disabled={running}>
              {running ? <><Icons.collect size={15} className="spin" /> Coletando…</> : <><Icons.play size={14} /> Rodar coleta</>}
            </button>
          </div>
          {(running || done) && (
            <div>
              <div className="bar" style={{ height: 8, marginBottom: 12 }}><span style={{ width: progress + '%', background: 'var(--accent)', transition: 'width .4s var(--ease)' }}></span></div>
              <div className="scroll" style={{ background: '#161009', borderRadius: 10, padding: '12px 14px', height: 168, fontFamily: 'var(--font-mono)', fontSize: '.76rem', lineHeight: 1.8, color: '#d6c6b4' }}>
                {logLines.map((l, i) => (
                  <div key={i} style={{ color: l.includes('timeout') ? '#e0a13e' : l.includes('concluída') ? '#36c0a4' : '#a8957f' }}>
                    <span style={{ color: '#82705d' }}>$</span> {l}
                  </div>
                ))}
                {running && <span style={{ color: '#e8772f' }}>▋</span>}
              </div>
            </div>
          )}
          {done && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 10, marginTop: 14 }}>
              {[['Coletados', done.collected, 'var(--muted)'], ['Novos', done.fresh, 'var(--accent-ink)'], ['Pontuados', done.scored, 'var(--ink)'], ['Alertas', done.alerts, 'var(--go)'], ['Erros', done.errors, 'var(--danger)']].map(([l, v, c]) => (
                <div key={l} style={{ textAlign: 'center', padding: '10px 4px', background: 'var(--bg-2)', borderRadius: 10, border: '1px solid var(--line)' }}>
                  <div className="tnum" style={{ fontSize: '1.4rem', fontWeight: 600, color: c }}>{v}</div>
                  <div className="field-label">{l}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Histórico (CollectionResult) */}
        <div className="card" style={{ overflow: 'hidden' }}>
          <div className="h-sec" style={{ padding: '15px 18px 10px' }}>Histórico de execuções</div>
          <table className="tbl">
            <thead><tr><th>Quando</th><th>Gatilho</th><th style={{ textAlign: 'right' }}>Coletados</th><th style={{ textAlign: 'right' }}>Novos</th><th style={{ textAlign: 'right' }}>Alertas</th><th style={{ textAlign: 'right' }}>Erros</th><th style={{ textAlign: 'right' }}>Tempo</th></tr></thead>
            <tbody>
              {window.DZ.runs.map(r => (
                <tr key={r.id} style={{ cursor: 'default' }}>
                  <td className="mono" style={{ fontSize: '.8rem', color: 'var(--ink)' }}>{r.at}</td>
                  <td><span className="chip" style={{ padding: '2px 8px', fontSize: '.72rem' }}>{r.trigger}</span></td>
                  <td className="tnum" style={{ textAlign: 'right' }}>{r.collected}</td>
                  <td className="tnum" style={{ textAlign: 'right', color: 'var(--accent-ink)', fontWeight: 600 }}>{r.fresh}</td>
                  <td className="tnum" style={{ textAlign: 'right', color: 'var(--go)' }}>{r.alerts}</td>
                  <td className="tnum" style={{ textAlign: 'right', color: r.errors ? 'var(--danger)' : 'var(--faint)' }}>{r.errors}</td>
                  <td className="tnum" style={{ textAlign: 'right', color: 'var(--muted)' }}>{r.secs}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Direita: fontes + scheduler */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div className="card" style={{ padding: '16px 18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
            <div className="h-sec">Agendador</div>
            <span className="reco reco-go"><span className="dot"></span>ativo</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 0', borderBottom: '1px solid var(--line)' }}>
            <Icons.clock size={18} style={{ color: 'var(--accent-ink)' }} />
            <div><div style={{ fontSize: '.88rem', fontWeight: 600, color: 'var(--ink)' }}>Diário · 06:00</div><div className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)' }}>cron via schedule · próxima: amanhã 06:00</div></div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.82rem', paddingTop: 12 }}>
            <span style={{ color: 'var(--muted)' }}>Última execução</span><span className="mono" style={{ color: 'var(--ink)' }}>hoje 06:00 · ok</span>
          </div>
        </div>

        <div className="card" style={{ padding: '16px 18px' }}>
          <div className="h-sec" style={{ marginBottom: 14 }}>Fontes de dados</div>
          {sources.map(s => (
            <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '11px 0', borderBottom: '1px solid var(--line)' }}>
              <span style={{ width: 9, height: 9, borderRadius: '50%', background: !s.enabled ? 'var(--faint)' : s.errors ? 'var(--review)' : 'var(--go)', flexShrink: 0 }}></span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '.88rem', fontWeight: 600, color: 'var(--ink)' }}>{s.name}</div>
                <div className="mono" style={{ fontSize: '.68rem', color: 'var(--faint)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.label}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                {s.enabled ? <div className="mono" style={{ fontSize: '.72rem', color: 'var(--muted)' }}>{s.new} novos · {s.last}</div> : <div className="mono" style={{ fontSize: '.72rem', color: 'var(--faint)' }}>desativada</div>}
                {s.errors ? <div className="mono" style={{ fontSize: '.68rem', color: 'var(--danger)' }}>{s.errors} erro</div> : null}
              </div>
              <span style={{ width: 34, height: 19, borderRadius: 20, background: s.enabled ? 'var(--accent)' : 'var(--line-2)', position: 'relative', flexShrink: 0, transition: '.2s' }}>
                <span style={{ position: 'absolute', top: 2, left: s.enabled ? 17 : 2, width: 15, height: 15, borderRadius: '50%', background: '#fff', transition: '.2s' }}></span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* Danzeroum — Alertas / Notificações */
function ScreenAlerts({ ctx }) {
  const [items, setItems] = useState(window.DZ.alerts);
  const levelTone = { go: 'go', review: 'review', danger: 'danger', skip: 'skip' };
  const kindIcon = { oportunidade: 'target', prazo: 'clock', documento: 'docs', coleta: 'collect' };
  const markAll = () => setItems(items.map(a => ({ ...a, read: true })));

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 16, alignItems: 'start' }}>
      <div className="card" style={{ overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 18px', borderBottom: '1px solid var(--line)' }}>
          <div className="h-sec">Central de alertas</div>
          <button className="btn btn-ghost btn-sm" onClick={markAll}>Marcar tudo como lido</button>
        </div>
        {items.map(a => {
          const KIcon = Icons[kindIcon[a.kind]] || Icons.bell;
          const tone = levelTone[a.level];
          return (
            <button key={a.id} onClick={() => { setItems(items.map(x => x.id === a.id ? { ...x, read: true } : x)); if (a.kind === 'documento') ctx.go('docs'); else if (a.ref && a.kind === 'oportunidade') { const t = window.DZ.tenders.find(t => t.id === a.ref); if (t) ctx.go('detail', t); } }}
              style={{ display: 'flex', gap: 13, width: '100%', textAlign: 'left', padding: '14px 18px', borderBottom: '1px solid var(--line)', background: a.read ? 'transparent' : 'var(--accent-wash)', transition: '.14s' }}>
              <span style={{ width: 36, height: 36, borderRadius: 9, flexShrink: 0, display: 'grid', placeItems: 'center', background: `var(--${tone}-wash)`, color: `var(--${tone})`, border: `1px solid var(--${tone}-line, var(--line))` }}><KIcon size={17} /></span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10 }}>
                  <span style={{ fontSize: '.9rem', fontWeight: 600, color: 'var(--ink)' }}>{a.title}</span>
                  <span className="mono" style={{ fontSize: '.68rem', color: 'var(--faint)', whiteSpace: 'nowrap' }}>{a.time}</span>
                </div>
                <div style={{ fontSize: '.82rem', color: 'var(--muted)', marginTop: 3 }}>{a.body}</div>
              </div>
              {!a.read && <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--brand)', flexShrink: 0, marginTop: 6 }}></span>}
            </button>
          );
        })}
      </div>

      <div className="card" style={{ padding: '16px 18px' }}>
        <div className="h-sec" style={{ marginBottom: 14 }}>Preferências de alerta</div>
        {[['Novas oportunidades GO', true], ['Oportunidades a revisar', true], ['Prazos a ≤ 3 dias', true], ['Certidões vencendo', true], ['Resumo diário por e-mail', true], ['Erros de coleta', false]].map(([l, on]) => (
          <div key={l} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid var(--line)' }}>
            <span style={{ fontSize: '.86rem', color: 'var(--text)' }}>{l}</span>
            <span style={{ width: 34, height: 19, borderRadius: 20, background: on ? 'var(--accent)' : 'var(--line-2)', position: 'relative', flexShrink: 0 }}>
              <span style={{ position: 'absolute', top: 2, left: on ? 17 : 2, width: 15, height: 15, borderRadius: '50%', background: '#fff' }}></span>
            </span>
          </div>
        ))}
        <div style={{ marginTop: 14, padding: 13, background: 'var(--bg-2)', borderRadius: 10, fontSize: '.8rem', color: 'var(--muted)', display: 'flex', gap: 9 }}>
          <Icons.bell size={16} style={{ flexShrink: 0, marginTop: 1, color: 'var(--accent-ink)' }} />
          Alertas disparam quando <b style={{ color: 'var(--ink)' }}>fit ≥ min_fit (0,60)</b> ou quando uma certidão entra na janela de vencimento.
        </div>
      </div>
    </div>
  );
}

window.ScreenCollect = ScreenCollect;
window.ScreenAlerts = ScreenAlerts;
