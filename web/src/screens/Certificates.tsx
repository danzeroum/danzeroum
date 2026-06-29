import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCertificates, uploadCertificate, deleteCertificate } from '../api/client'

function fmtBRL(n: number | null): string {
  if (!n || n <= 0) return '—'
  if (n >= 1_000_000) return `R$ ${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `R$ ${(n / 1_000).toFixed(0)}k`
  return `R$ ${n.toFixed(2)}`
}

export default function Certificates() {
  const qc = useQueryClient()
  const { data = [], isLoading } = useQuery({ queryKey: ['certificates'], queryFn: getCertificates })
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ client_name: '', project_description: '', start_date: '', end_date: '', project_value: '' })
  const [file, setFile] = useState<File | null>(null)

  const upload = useMutation({
    mutationFn: (fd: FormData) => uploadCertificate(fd),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['certificates'] }); setShowModal(false) },
  })

  const del = useMutation({
    mutationFn: deleteCertificate,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['certificates'] }),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const fd = new FormData()
    fd.append('client_name', form.client_name)
    if (form.project_description) fd.append('project_description', form.project_description)
    if (form.start_date) fd.append('start_date', form.start_date)
    if (form.end_date) fd.append('end_date', form.end_date)
    if (form.project_value) fd.append('project_value', form.project_value)
    if (file) fd.append('file', file)
    upload.mutate(fd)
  }

  return (
    <div className="page fade-up">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 22 }}>
        <h1 className="h-page">Atestados Técnicos</h1>
        <button className="btn" onClick={() => setShowModal(true)}>+ Novo atestado</button>
      </div>

      {isLoading
        ? <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 14 }}>{[0,1,2,3].map(i => <div key={i} className="card" style={{ height: 120, opacity: .4 }} />)}</div>
        : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 14 }}>
            {data.map(cert => (
              <div key={cert.id} className="card fade-in" style={{ padding: '16px 20px', position: 'relative' }}>
                <button onClick={() => del.mutate(cert.id)} style={{ position: 'absolute', top: 10, right: 14, background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: '1.1rem' }}>×</button>
                <p style={{ fontWeight: 600, marginBottom: 4, paddingRight: 20 }}>{cert.client_name ?? '—'}</p>
                <p style={{ fontSize: '.84rem', color: 'var(--muted)', marginBottom: 8 }}>{cert.project_description ?? '—'}</p>
                <div style={{ display: 'flex', gap: 16, fontSize: '.8rem', color: 'var(--faint)' }}>
                  <span>{cert.start_date ?? '—'} → {cert.end_date ?? '—'}</span>
                  <span className="tnum">{fmtBRL(cert.project_value)}</span>
                </div>
                {cert.file_name && (
                  <a href={`/api/certificates/${cert.id}/file`} target="_blank" rel="noreferrer" style={{ display: 'block', marginTop: 8, fontSize: '.78rem', color: 'var(--accent)' }}>{cert.file_name}</a>
                )}
              </div>
            ))}
            {!data.length && <p style={{ color: 'var(--muted)', gridColumn: '1/-1', padding: 32, textAlign: 'center' }}>Nenhum atestado cadastrado</p>}
          </div>
        )
      }

      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.45)', display: 'grid', placeItems: 'center', zIndex: 100 }}>
          <div className="card fade-in" style={{ width: 460, padding: '28px 32px' }}>
            <h2 className="h-sec" style={{ marginBottom: 20 }}>Novo atestado técnico</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <label className="field-label">Cliente *
                <input required value={form.client_name} onChange={e => setForm(f => ({ ...f, client_name: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
              </label>
              <label className="field-label">Descrição do projeto
                <textarea value={form.project_description} onChange={e => setForm(f => ({ ...f, project_description: e.target.value }))} rows={2} style={{ display: 'block', width: '100%', marginTop: 4, resize: 'vertical' }} />
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <label className="field-label">Início
                  <input type="date" value={form.start_date} onChange={e => setForm(f => ({ ...f, start_date: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
                </label>
                <label className="field-label">Fim
                  <input type="date" value={form.end_date} onChange={e => setForm(f => ({ ...f, end_date: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
                </label>
              </div>
              <label className="field-label">Valor do projeto (R$)
                <input type="number" value={form.project_value} onChange={e => setForm(f => ({ ...f, project_value: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
              </label>
              <label className="field-label">Arquivo (PDF)
                <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={e => setFile(e.target.files?.[0] ?? null)} style={{ display: 'block', marginTop: 4 }} />
              </label>
              <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
                <button type="submit" className="btn" disabled={upload.isPending}>{upload.isPending ? 'Salvando…' : 'Salvar'}</button>
                <button type="button" className="btn" style={{ background: 'var(--bg-2)', color: 'var(--text)' }} onClick={() => setShowModal(false)}>Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
