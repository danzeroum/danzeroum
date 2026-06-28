import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { startCollection, getRunStatus, getCollectRuns } from '../api/client'
import { Icons } from '../components/icons'
import type { CollectionRunStatus } from '../api/types'

function StatusDot({ status }: { status: string }) {
  const color = status === 'done' ? 'var(--go)' : status === 'error' ? 'var(--danger)' : 'var(--review)'
  return <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: color, marginRight: 6 }} />
}

export default function Collect() {
  const [runId, setRunId] = useState<string | null>(null)
  const [logLines, setLogLines] = useState<string[]>([])
  const logRef = useRef<HTMLDivElement>(null)

  const { data: runs, refetch: refetchRuns } = useQuery({
    queryKey: ['collect-runs'],
    queryFn: getCollectRuns,
    refetchInterval: runId ? 3_000 : false,
  })

  const { data: runStatus } = useQuery({
    queryKey: ['run-status', runId],
    queryFn: () => getRunStatus(runId!),
    enabled: !!runId,
    refetchInterval: (query) => {
      const data = query.state.data as CollectionRunStatus | undefined
      return data?.status === 'running' ? 2_000 : false
    },
  })

  const startMutation = useMutation({
    mutationFn: startCollection,
    onSuccess: (data) => {
      setRunId(data.run_id)
      setLogLines([`[${new Date().toLocaleTimeString('pt-BR')}] Coleta iniciada — run_id: ${data.run_id}`])
      refetchRuns()
    },
  })

  // Append log lines as run progresses
  useEffect(() => {
    if (!runStatus) return
    if (runStatus.status === 'done' && runStatus.result) {
      const r = runStatus.result
      if (!('error' in r)) {
        setLogLines(prev => [
          ...prev,
          `[${new Date().toLocaleTimeString('pt-BR')}] Coletados: ${r.collected} editais`,
          `[${new Date().toLocaleTimeString('pt-BR')}] Novos: ${r.new} | Pontuados: ${r.scored}`,
          ...(r.errors?.map((e: {source?: string; message?: string}) => `[ERRO] ${e.source ?? ''}: ${e.message ?? JSON.stringify(e)}`) ?? []),
          `[${new Date().toLocaleTimeString('pt-BR')}] Coleta concluída ✓`,
        ])
      }
    }
    if (runStatus.status === 'error' && runStatus.result) {
      setLogLines(prev => [...prev, `[ERRO] ${runStatus.result!.error ?? 'Erro desconhecido'}`])
    }
    refetchRuns()
  }, [runStatus?.status, refetchRuns])

  // Auto-scroll log
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [logLines])

  const isRunning = runStatus?.status === 'running' || startMutation.isPending

  return (
    <div className="page fade-up">
      <h1 className="h-page" style={{ marginBottom: 22 }}>Coleta de Dados</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 20, alignItems: 'start' }}>
        {/* Left — run panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card" style={{ padding: '20px 22px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
              <div>
                <h2 className="h-sec">Iniciar Coleta</h2>
                <p style={{ fontSize: '.84rem', color: 'var(--muted)', marginTop: 4 }}>Coleta de todas as fontes habilitadas, deduplicação e scoring automático</p>
              </div>
              <button
                className="btn btn-primary"
                style={{ marginLeft: 'auto', gap: 8, whiteSpace: 'nowrap' }}
                onClick={() => startMutation.mutate()}
                disabled={isRunning}
              >
                <Icons.collect size={15} />
                {isRunning ? 'Coletando…' : 'Iniciar coleta'}
              </button>
            </div>

            {/* Progress */}
            {isRunning && (
              <div style={{ marginBottom: 16 }}>
                <div className="bar" style={{ marginBottom: 8 }}>
                  <span style={{ width: '100%', background: 'var(--accent)', animation: 'spin 1.5s linear infinite', transformOrigin: 'center' }} />
                </div>
                <p style={{ fontSize: '.8rem', color: 'var(--muted)' }}>Coletando dados…</p>
              </div>
            )}

            {/* Log terminal */}
            <div
              ref={logRef}
              className="scroll"
              style={{
                background: 'var(--bg)', border: '1px solid var(--line)', borderRadius: 'var(--radius)',
                padding: '12px 14px', minHeight: 180, maxHeight: 280, fontFamily: 'var(--font-mono)',
                fontSize: '.76rem', lineHeight: 1.7, color: 'var(--text)',
              }}
            >
              {logLines.length === 0
                ? <span style={{ color: 'var(--faint)' }}>$ aguardando coleta…</span>
                : logLines.map((line, i) => (
                  <div key={i} style={{ color: line.startsWith('[ERRO]') ? 'var(--danger)' : line.includes('✓') ? 'var(--go)' : 'inherit' }}>
                    {line}
                  </div>
                ))
              }
            </div>
          </div>

          {/* Run result summary */}
          {runStatus?.status === 'done' && runStatus.result && !('error' in runStatus.result) && (
            <div className="card" style={{ padding: '16px 20px' }}>
              <h2 className="h-sec" style={{ marginBottom: 14 }}>Resultado</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12 }}>
                {[
                  { label: 'Coletados', val: runStatus.result.collected },
                  { label: 'Novos', val: runStatus.result.new },
                  { label: 'Pontuados', val: runStatus.result.scored },
                  { label: 'Erros', val: runStatus.result.errors?.length ?? 0 },
                ].map(({ label, val }) => (
                  <div key={label} style={{ textAlign: 'center' }}>
                    <p className="eyebrow" style={{ marginBottom: 4 }}>{label}</p>
                    <p style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '1.4rem', color: 'var(--ink)' }}>{val}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right — history */}
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--line)' }}>
            <h2 className="h-sec">Histórico de execuções</h2>
          </div>
          <div className="scroll" style={{ maxHeight: 480 }}>
            {!runs?.length && (
              <p style={{ padding: 24, color: 'var(--muted)', fontSize: '.88rem', textAlign: 'center' }}>Nenhuma execução nesta sessão</p>
            )}
            {runs?.map((run, i) => (
              <div key={run.run_id} style={{ padding: '12px 18px', borderBottom: '1px solid var(--line)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <StatusDot status={run.status} />
                  <span style={{ fontSize: '.82rem', fontFamily: 'var(--font-mono)', color: 'var(--faint)' }}>#{runs.length - i}</span>
                  <span style={{ fontSize: '.82rem', color: 'var(--text)', marginLeft: 4 }}>
                    {run.status === 'running' ? 'Em andamento' : run.status === 'done' ? 'Concluída' : 'Erro'}
                  </span>
                </div>
                {run.result && !('error' in run.result) && (
                  <div style={{ fontSize: '.8rem', color: 'var(--muted)', display: 'flex', gap: 12 }}>
                    <span>{run.result.collected} coletados</span>
                    <span>{run.result.new} novos</span>
                    <span>{run.result.scored} pontuados</span>
                  </div>
                )}
                {run.result?.error && (
                  <p style={{ fontSize: '.8rem', color: 'var(--danger)' }}>{run.result.error}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
