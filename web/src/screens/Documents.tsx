import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getDocuments, uploadDocument, deleteDocument } from '../api/client'
import type { Document } from '../api/types'

function statusLabel(doc: Document): { label: string; color: string } {
  if (!doc.expiry_date) return { label: 'Sem prazo', color: 'var(--muted)' }
  const days = Math.ceil((new Date(doc.expiry_date).getTime() - Date.now()) / 86400000)
  if (!doc.is_valid || days < 0) return { label: 'Vencido', color: 'var(--danger)' }
  if (days <= 30) return { label: `Vence em ${days}d`, color: 'var(--review)' }
  return { label: 'Válido', color: 'var(--go)' }
}

export default function Documents() {
  const qc = useQueryClient()
  const { data = [], isLoading } = useQuery({ queryKey: ['documents'], queryFn: () => getDocuments() })
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ type: 'CND', name: '', expiry_date: '' })
  const [file, setFile] = useState<File | null>(null)

  const upload = useMutation({
    mutationFn: (fd: FormData) => uploadDocument(fd),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['documents'] }); setShowModal(false) },
  })

  const del = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents'] }),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const fd = new FormData()
    fd.append('type', form.type)
    if (form.name) fd.append('name', form.name)
    if (form.expiry_date) fd.append('expiry_date', form.expiry_date)
    if (file) fd.append('file', file)
    upload.mutate(fd)
  }

  return (
    <div className="page fade-up">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 22 }}>
        <h1 className="h-page">Documentos</h1>
        <button className="btn" onClick={() => setShowModal(true)}>+ Novo documento</button>
      </div>

      {isLoading ? <div className="card" style={{ height: 200, opacity: .4 }} /> : (
        <div className="card" style={{ overflow: 'hidden' }}>
          <div className="scroll">
            <table className="tbl">
              <thead><tr>
                <th>Tipo</th><th>Nome</th><th>Válido até</th><th>Status</th><th>Arquivo</th><th></th>
              </tr></thead>
              <tbody>
                {data.map(doc => {
                  const s = statusLabel(doc)
                  return (
                    <tr key={doc.id}>
                      <td><span className="tnum" style={{ fontSize: '.78rem', color: 'var(--faint)' }}>{doc.type}</span></td>
                      <td>{doc.name ?? '—'}</td>
                      <td className="tnum" style={{ fontSize: '.84rem' }}>{doc.expiry_date ?? '—'}</td>
                      <td><span style={{ fontSize: '.78rem', color: s.color, fontWeight: 600 }}>{s.label}</span></td>
                      <td>{doc.file_name
                        ? <a href={`/api/documents/${doc.id}/file`} target="_blank" rel="noreferrer" style={{ fontSize: '.8rem', color: 'var(--accent)' }}>{doc.file_name}</a>
                        : <span style={{ color: 'var(--faint)', fontSize: '.8rem' }}>—</span>}
                      </td>
                      <td><button className="btn-sm" style={{ color: 'var(--danger)' }} onClick={() => del.mutate(doc.id)}>×</button></td>
                    </tr>
                  )
                })}
                {!data.length && <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--muted)', padding: 32 }}>Nenhum documento cadastrado</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.45)', display: 'grid', placeItems: 'center', zIndex: 100 }}>
          <div className="card fade-in" style={{ width: 420, padding: '28px 32px' }}>
            <h2 className="h-sec" style={{ marginBottom: 20 }}>Novo documento</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <label className="field-label">Tipo
                <select value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }}>
                  {['CND','CNDT','FGTS','Alvará','ISS','Contrato Social','Procuração','Outro'].map(t => <option key={t}>{t}</option>)}
                </select>
              </label>
              <label className="field-label">Nome
                <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Ex: CND Federal" style={{ display: 'block', width: '100%', marginTop: 4 }} />
              </label>
              <label className="field-label">Válido até
                <input type="date" value={form.expiry_date} onChange={e => setForm(f => ({ ...f, expiry_date: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
              </label>
              <label className="field-label">Arquivo (PDF/imagem)
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
