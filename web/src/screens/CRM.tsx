import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getClients, createClient, patchClient, deleteClient } from '../api/client'
import type { Client } from '../api/types'

const COLUMNS = [
  { key: 'LEAD', label: 'Lead', color: 'var(--accent)' },
  { key: 'CLIENT', label: 'Cliente', color: 'var(--go)' },
  { key: 'ARCHIVED', label: 'Arquivado', color: 'var(--faint)' },
]

export default function CRM() {
  const qc = useQueryClient()
  const { data = [], isLoading } = useQuery({ queryKey: ['clients'], queryFn: () => getClients() })
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ name: '', cnpj: '', contact_name: '', email: '', phone: '' })

  const create = useMutation({
    mutationFn: () => createClient({
      name: form.name,
      cnpj: form.cnpj || undefined,
      contact_name: form.contact_name || undefined,
      email: form.email || undefined,
      phone: form.phone || undefined,
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['clients'] })
      setShowModal(false)
      setForm({ name: '', cnpj: '', contact_name: '', email: '', phone: '' })
    },
  })

  const patch = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => patchClient(id, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  })

  const del = useMutation({
    mutationFn: deleteClient,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  })

  const byStatus: Record<string, Client[]> = {}
  for (const col of COLUMNS) byStatus[col.key] = data.filter(c => c.status === col.key)

  if (isLoading) return <div className="page"><div className="card" style={{ height: 300, opacity: .4 }} /></div>

  return (
    <div className="page fade-up">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 22 }}>
        <h1 className="h-page">CRM — Clientes</h1>
        <button className="btn" onClick={() => setShowModal(true)}>+ Novo cliente</button>
      </div>

      <div style={{ display: 'flex', gap: 16 }}>
        {COLUMNS.map(col => (
          <div key={col.key} style={{ flex: 1, minWidth: 240 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: col.color, flexShrink: 0 }} />
              <span style={{ fontWeight: 600, fontSize: '.88rem' }}>{col.label}</span>
              <span style={{ marginLeft: 'auto', fontSize: '.78rem', color: 'var(--muted)' }}>{byStatus[col.key].length}</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {byStatus[col.key].map(c => (
                <div key={c.id} className="card fade-in" style={{ padding: '14px 16px' }}>
                  <p style={{ fontWeight: 600, marginBottom: 2 }}>{c.name}</p>
                  {c.contact_name && <p style={{ fontSize: '.82rem', color: 'var(--muted)' }}>{c.contact_name}</p>}
                  {c.email && <p style={{ fontSize: '.78rem', color: 'var(--faint)' }}>{c.email}</p>}
                  {c.cnpj && <p className="tnum" style={{ fontSize: '.74rem', color: 'var(--faint)', marginTop: 4 }}>{c.cnpj}</p>}
                  <div style={{ display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap' }}>
                    {COLUMNS.filter(cl => cl.key !== col.key).map(cl => (
                      <button key={cl.key} className="btn-sm" onClick={() => patch.mutate({ id: c.id, status: cl.key })} style={{ fontSize: '.7rem' }}>→ {cl.label}</button>
                    ))}
                    <button className="btn-sm" onClick={() => del.mutate(c.id)} style={{ color: 'var(--danger)', fontSize: '.7rem' }}>×</button>
                  </div>
                </div>
              ))}
              {!byStatus[col.key].length && (
                <div style={{ border: '2px dashed var(--line)', borderRadius: 8, padding: 24, textAlign: 'center', color: 'var(--faint)', fontSize: '.78rem' }}>vazio</div>
              )}
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.45)', display: 'grid', placeItems: 'center', zIndex: 100 }}>
          <div className="card fade-in" style={{ width: 440, padding: '28px 32px' }}>
            <h2 className="h-sec" style={{ marginBottom: 20 }}>Novo cliente / lead</h2>
            <form onSubmit={e => { e.preventDefault(); create.mutate() }} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <label className="field-label">Nome *
                <input required value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
              </label>
              <label className="field-label">CNPJ
                <input value={form.cnpj} onChange={e => setForm(f => ({ ...f, cnpj: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
              </label>
              <label className="field-label">Contato
                <input value={form.contact_name} onChange={e => setForm(f => ({ ...f, contact_name: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <label className="field-label">E-mail
                  <input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
                </label>
                <label className="field-label">Telefone
                  <input value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} style={{ display: 'block', width: '100%', marginTop: 4 }} />
                </label>
              </div>
              <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
                <button type="submit" className="btn" disabled={create.isPending}>{create.isPending ? 'Salvando…' : 'Salvar'}</button>
                <button type="button" className="btn" style={{ background: 'var(--bg-2)', color: 'var(--text)' }} onClick={() => setShowModal(false)}>Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
