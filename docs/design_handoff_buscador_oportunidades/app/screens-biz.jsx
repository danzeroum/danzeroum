/* Danzeroum — Propostas (kanban) */
const PSTAGES = [
  { id: 'DRAFT', label: 'Rascunho', tone: 'skip' },
  { id: 'SENT', label: 'Enviada', tone: 'review' },
  { id: 'UNDER_REVIEW', label: 'Em análise', tone: 'review' },
  { id: 'WIN', label: 'Ganha', tone: 'go' },
  { id: 'LOST', label: 'Perdida', tone: 'skip' },
  { id: 'DISQUALIFIED', label: 'Desclassificada', tone: 'danger' },
];

function ScreenProposals() {
  const [items, setItems] = useState(window.DZ.proposals);
  const [drag, setDrag] = useState(null);

  const drop = (stage) => {
    if (drag) setItems(items.map(p => p.id === drag ? { ...p, status: stage } : p));
    setDrag(null);
  };
  const total = (st) => items.filter(p => p.status === st).reduce((s, p) => s + p.value, 0);
  const won = total('WIN');

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 16 }}>
        {[['Em aberto', items.filter(p => ['DRAFT', 'SENT', 'UNDER_REVIEW'].includes(p.status)).length, 'var(--accent-ink)'], ['Ganhas', items.filter(p => p.status === 'WIN').length, 'var(--go)'], ['Valor ganho', window.DZ.fmtBRLk(won), 'var(--go)'], ['Taxa de vitória', Math.round(items.filter(p => p.status === 'WIN').length / Math.max(1, items.filter(p => ['WIN', 'LOST', 'DISQUALIFIED'].includes(p.status)).length) * 100) + '%', 'var(--ink)']].map(([l, v, c]) => (
          <div key={l} className="card" style={{ padding: '13px 16px' }}>
            <div className="field-label">{l}</div>
            <div className="tnum" style={{ fontSize: '1.5rem', fontWeight: 600, color: c, marginTop: 4 }}>{v}</div>
          </div>
        ))}
      </div>

      <div className="scroll" style={{ overflowX: 'auto', paddingBottom: 8 }}>
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${PSTAGES.length}, minmax(208px, 1fr))`, gap: 12, minWidth: 1180 }}>
          {PSTAGES.map(stage => {
            const cards = items.filter(p => p.status === stage.id);
            return (
              <div key={stage.id} className="kcol" onDragOver={e => e.preventDefault()} onDrop={() => drop(stage.id)} style={{ outline: drag ? '1.5px dashed var(--line-2)' : 'none', outlineOffset: -4 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 13px 9px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: `var(--${stage.tone})` }}></span>
                    <span style={{ fontSize: '.82rem', fontWeight: 600, color: 'var(--ink)' }}>{stage.label}</span>
                    <span className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)' }}>{cards.length}</span>
                  </div>
                </div>
                <div className="scroll" style={{ padding: '0 9px 12px', display: 'flex', flexDirection: 'column', gap: 9, minHeight: 60 }}>
                  {cards.map(p => (
                    <div key={p.id} className="kcard" draggable onDragStart={() => setDrag(p.id)} onDragEnd={() => setDrag(null)} style={{ opacity: drag === p.id ? .4 : 1 }}>
                      <div style={{ fontSize: '.84rem', fontWeight: 600, color: 'var(--ink)', lineHeight: 1.3 }}>{p.title}</div>
                      <div className="mono" style={{ fontSize: '.66rem', color: 'var(--faint)', marginTop: 5 }}>{p.tender} · {p.version}</div>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 10 }}>
                        <span className="tnum" style={{ fontSize: '.86rem', fontWeight: 600, color: 'var(--ink)' }}>{window.DZ.fmtBRLk(p.value)}</span>
                        <span className="mono" style={{ fontSize: '.66rem', color: 'var(--muted)' }}>val. {window.DZ.fmtDate(p.validity)}</span>
                      </div>
                    </div>
                  ))}
                  {cards.length === 0 && <div style={{ fontSize: '.74rem', color: 'var(--faint)', textAlign: 'center', padding: '14px 0' }}>—</div>}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="mono" style={{ fontSize: '.72rem', color: 'var(--faint)', marginTop: 12, textAlign: 'center' }}>Arraste os cartões entre colunas para mudar o status da proposta.</div>
    </div>
  );
}

/* Danzeroum — Calculadora de preço mínimo (Fator R · Simples Nacional) */
function ScreenCalc() {
  const [folha, setFolha] = useState(38);   // % folha sobre receita
  const [receita, setReceita] = useState(2480000);
  const [custoDireto, setCusto] = useState(54); // % custo direto
  const [margem, setMargem] = useState(22);

  const fatorR = folha / 100;
  const anexo = fatorR >= 0.28 ? 'III' : 'IV';
  const aliquota = anexo === 'III' ? 16.0 : 19.5; // efetiva ilustrativa
  const tributos = receita * (aliquota / 100);
  const custo = receita * (custoDireto / 100);
  const precoMin = (custo + tributos) / (1 - margem / 100);
  const margemReais = precoMin - custo - tributos;

  const Slider = ({ label, value, set, min, max, step, suffix }) => (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <span className="field-label">{label}</span>
        <span className="mono" style={{ fontSize: '.82rem', fontWeight: 600, color: 'var(--accent-ink)' }}>{value}{suffix}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={e => set(+e.target.value)} style={{ accentColor: 'var(--accent)', width: '100%' }} />
    </div>
  );

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.1fr', gap: 16, alignItems: 'start' }}>
      <div className="card" style={{ padding: '20px 22px' }}>
        <div className="h-sec" style={{ marginBottom: 4 }}>Parâmetros</div>
        <div style={{ fontSize: '.82rem', color: 'var(--muted)', marginBottom: 18 }}>Entradas do edital e da estrutura de custo da empresa.</div>
        <div style={{ marginBottom: 18 }}>
          <div className="field-label" style={{ marginBottom: 8 }}>Receita / valor de referência</div>
          <input className="input mono" value={window.DZ.fmtBRL(receita)} onChange={e => { const n = +e.target.value.replace(/\D/g, ''); if (!isNaN(n)) setReceita(n); }} />
        </div>
        <Slider label="Folha de pagamento (12 meses / receita)" value={folha} set={setFolha} min={10} max={60} step={1} suffix="%" />
        <Slider label="Custo direto do projeto" value={custoDireto} set={setCusto} min={20} max={80} step={1} suffix="%" />
        <Slider label="Margem-alvo" value={margem} set={setMargem} min={5} max={40} step={1} suffix="%" />

        <div style={{ marginTop: 6, padding: 14, borderRadius: 11, background: fatorR >= 0.28 ? 'var(--go-wash)' : 'var(--review-wash)', border: `1px solid ${fatorR >= 0.28 ? 'var(--go-line)' : 'var(--review-line)'}` }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span className="field-label">Fator R</span>
            <span className="mono" style={{ fontWeight: 600, color: fatorR >= 0.28 ? 'var(--go)' : 'var(--review)' }}>{fatorR.toFixed(2)}</span>
          </div>
          <div style={{ fontSize: '.82rem', color: 'var(--text)', marginTop: 6 }}>
            {fatorR >= 0.28 ? <>Folha ≥ 28% → tributação pelo <b style={{ color: 'var(--ink)' }}>Anexo III</b> (alíquota menor).</> : <>Folha &lt; 28% → tributação pelo <b style={{ color: 'var(--ink)' }}>Anexo IV</b> (alíquota maior).</>}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '20px 22px', background: 'var(--navy)', color: '#fff' }}>
            <div className="field-label" style={{ color: 'rgba(255,255,255,.6)' }}>Preço mínimo viável</div>
            <div className="tnum" style={{ fontSize: '2.4rem', fontWeight: 600, letterSpacing: '-.02em', marginTop: 4 }}>{window.DZ.fmtBRL(Math.round(precoMin))}</div>
            <div style={{ fontSize: '.82rem', color: 'rgba(255,255,255,.7)', marginTop: 4 }}>Anexo {anexo} · alíquota efetiva {aliquota.toFixed(1)}% · margem {margem}%</div>
          </div>
          <div style={{ padding: '6px 22px' }}>
            {[['Custo direto', custo, custoDireto + '% da receita'], ['Carga tributária (Simples)', tributos, `Anexo ${anexo} · ${aliquota.toFixed(1)}%`], ['Margem', margemReais, margem + '% sobre o preço']].map(([l, v, sub], i) => (
              <div key={l} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 0', borderBottom: i < 2 ? '1px solid var(--line)' : 'none' }}>
                <div><div style={{ fontSize: '.88rem', fontWeight: 500, color: 'var(--ink)' }}>{l}</div><div className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)', marginTop: 2 }}>{sub}</div></div>
                <span className="tnum" style={{ fontSize: '.96rem', fontWeight: 600, color: 'var(--ink)' }}>{window.DZ.fmtBRL(Math.round(v))}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="card" style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 11 }}>
          <Icons.alert size={18} style={{ color: 'var(--review)', flexShrink: 0 }} />
          <span style={{ fontSize: '.8rem', color: 'var(--muted)' }}>Alíquotas efetivas são ilustrativas. Confirme a faixa do Simples (RBT12) antes de fechar a proposta.</span>
        </div>
        <button className="btn btn-primary" style={{ justifyContent: 'center' }}><Icons.proposals size={15} /> Usar este preço na proposta</button>
      </div>
    </div>
  );
}

/* Danzeroum — CRM / Clientes */
const CRM_STAGES = [
  { id: 'qualificacao', label: 'Qualificação' },
  { id: 'oportunidade', label: 'Oportunidade' },
  { id: 'proposta', label: 'Proposta' },
  { id: 'cliente', label: 'Cliente' },
];
function ScreenCRM({ ctx }) {
  const clients = window.DZ.clients;
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ fontSize: '.86rem', color: 'var(--muted)' }}>Funil comercial — órgãos e leads vinculados às oportunidades.</div>
        <button className="btn btn-primary btn-sm"><Icons.plus size={14} /> Novo cliente</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 }}>
        {CRM_STAGES.map(stage => {
          const col = clients.filter(c => c.stage === stage.id);
          const sum = col.reduce((s, c) => s + c.value, 0);
          return (
            <div key={stage.id} className="kcol">
              <div style={{ padding: '13px 14px 10px', borderBottom: '1px solid var(--line)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '.84rem', fontWeight: 600, color: 'var(--ink)' }}>{stage.label}</span>
                  <span className="mono" style={{ fontSize: '.7rem', color: 'var(--faint)' }}>{col.length}</span>
                </div>
                <div className="tnum" style={{ fontSize: '.78rem', color: 'var(--accent-ink)', marginTop: 3 }}>{window.DZ.fmtBRLk(sum)}</div>
              </div>
              <div style={{ padding: 10, display: 'flex', flexDirection: 'column', gap: 9 }}>
                {col.map(c => (
                  <div key={c.id} className="kcard" style={{ cursor: 'default' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ width: 28, height: 28, borderRadius: 7, background: 'var(--navy)', color: '#fff', display: 'grid', placeItems: 'center', fontSize: '.62rem', fontWeight: 600, flexShrink: 0 }}>{c.uf}</span>
                      <span style={{ fontSize: '.83rem', fontWeight: 600, color: 'var(--ink)', lineHeight: 1.25 }}>{c.name}</span>
                    </div>
                    <div className="mono" style={{ fontSize: '.66rem', color: 'var(--faint)', marginTop: 8 }}>{c.contact}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                      <span className="tnum" style={{ fontSize: '.8rem', fontWeight: 600, color: 'var(--ink)' }}>{window.DZ.fmtBRLk(c.value)}</span>
                      <span className="mono" style={{ fontSize: '.64rem', color: 'var(--faint)' }}>{c.tenders} {c.tenders > 1 ? 'editais' : 'edital'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

window.ScreenProposals = ScreenProposals;
window.ScreenCalc = ScreenCalc;
window.ScreenCRM = ScreenCRM;
