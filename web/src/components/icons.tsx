import type { SVGProps, ReactNode } from 'react'

type IcProps = SVGProps<SVGSVGElement> & {
  d?: string
  fill?: string
  size?: number
  sw?: number
  children?: ReactNode
}

function Ic({ d, fill, size = 18, sw = 2, children, ...p }: IcProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={fill ?? 'none'}
      stroke={fill ? 'none' : 'currentColor'}
      strokeWidth={sw}
      strokeLinecap="round"
      strokeLinejoin="round"
      {...p}
    >
      {d ? <path d={d} /> : children}
    </svg>
  )
}

type IconFn = (p?: IcProps) => React.ReactElement

import React from 'react'

export const Icons: Record<string, IconFn> = {
  dashboard: (p) => <Ic {...p}><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></Ic>,
  list: (p) => <Ic {...p}><path d="M8 6h13M8 12h13M8 18h13M3.5 6h.01M3.5 12h.01M3.5 18h.01"/></Ic>,
  collect: (p) => <Ic {...p}><path d="M21 12a9 9 0 1 1-9-9c2.5 0 4.8 1 6.4 2.6"/><path d="M21 4v4h-4"/></Ic>,
  bell: (p) => <Ic {...p}><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></Ic>,
  config: (p) => <Ic {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 0 1-4 0v-.1A1.6 1.6 0 0 0 7 19.4a1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 2.6 14H2.5a2 2 0 0 1 0-4h.1A1.6 1.6 0 0 0 4 7a1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.6 1.6 0 0 0 9 2.6V2.5a2 2 0 0 1 4 0v.1A1.6 1.6 0 0 0 17 4.6a1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A1.6 1.6 0 0 0 21.4 9h.1a2 2 0 0 1 0 4h-.1a1.6 1.6 0 0 0-1.1.99z"/></Ic>,
  search: (p) => <Ic {...p}><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></Ic>,
  sun: (p) => <Ic {...p}><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></Ic>,
  moon: (p) => <Ic {...p}><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></Ic>,
  close: (p) => <Ic {...p}><path d="M18 6 6 18M6 6l12 12"/></Ic>,
  play: (p) => <Ic {...p}><path d="M6 4l14 8-14 8z" fill="currentColor" stroke="none"/></Ic>,
  clock: (p) => <Ic {...p}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></Ic>,
  alert: (p) => <Ic {...p}><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></Ic>,
  plus: (p) => <Ic {...p}><path d="M12 5v14M5 12h14"/></Ic>,
  ext: (p) => <Ic {...p}><path d="M15 3h6v6M21 3l-9 9M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5"/></Ic>,
  trend: (p) => <Ic {...p}><path d="M3 17l6-6 4 4 8-8"/><path d="M21 7v5M21 7h-5"/></Ic>,
  money: (p) => <Ic {...p}><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/></Ic>,
  layers: (p) => <Ic {...p}><path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/></Ic>,
  check: (p) => <Ic {...p}><path d="M20 6 9 17l-5-5"/></Ic>,
  chevR: (p) => <Ic {...p}><path d="m9 6 6 6-6 6"/></Ic>,
  docs: (p) => <Ic {...p}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></Ic>,
  certs: (p) => <Ic {...p}><circle cx="12" cy="8" r="6"/><path d="M15.5 15.5 17 22l-5-3-5 3 1.5-6.5"/></Ic>,
  proposals: (p) => <Ic {...p}><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></Ic>,
  crm: (p) => <Ic {...p}><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></Ic>,
  calc: (p) => <Ic {...p}><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="10" y2="10"/><line x1="14" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="10" y2="14"/><line x1="14" y1="14" x2="16" y2="14"/></Ic>,
}

export function Logo({ size = 30, dark = false }: { size?: number; dark?: boolean }) {
  const stroke = dark ? '#e8772f' : '#24324a'
  const fill = dark ? '#e8772f' : '#bd4e1c'
  const shieldFill = dark ? '#fbf7f1' : '#24324a'
  const shieldStroke = dark ? '#24324a' : '#fbf7f1'
  return (
    <svg width={size} height={size * 0.78} viewBox="-10 0 80 64" aria-label="Danzeroum">
      <g fill="none" stroke={stroke} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        <path d="M-8 21 L1 26"/><path d="M1 26 L10 31"/><path d="M-8 43 L1 38"/><path d="M1 38 L10 33"/>
        <path d="M49 32 L60 19"/><path d="M49 32 H62"/><path d="M49 32 L60 45"/>
      </g>
      <g fill={stroke}>
        <circle cx="-9" cy="20" r="2.4"/><circle cx="-9" cy="44" r="2.4"/>
        <circle cx="62" cy="18" r="2.6"/><circle cx="64" cy="32" r="2.6"/><circle cx="62" cy="46" r="2.6"/>
      </g>
      <path d="M10 11 H28 C41 11 49 20.5 49 32 C49 43.5 40 53 28 53 H10 Z" fill={fill}/>
      <path d="M27 18 L37 21.6 V31 C37 38 32.5 42.4 27 45 C21.5 42.4 17 38 17 31 V21.6 Z"
        fill={shieldFill} stroke={shieldStroke} strokeWidth="2.4" strokeLinejoin="round"/>
      <path d="M21.8 31 L25.2 34.4 L31 28" fill="none" stroke={shieldStroke}
        strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}

export function RecoTag({ rec, sm }: { rec: string; sm?: boolean }) {
  const map: Record<string, [string, string]> = {
    GO: ['reco reco-go', 'GO'],
    REVIEW: ['reco reco-review', 'Revisar'],
    SKIP: ['reco reco-skip', 'Pular'],
  }
  const [cls, label] = map[rec] ?? map.SKIP
  const style = sm ? { fontSize: '.58rem', padding: '2px 6px' } : undefined
  return <span className={cls} style={style}><span className="dot" />{label}</span>
}

export function Gauge({ value, label, tone = 'accent', size = 64 }: {
  value: number | null; label: string; tone?: string; size?: number
}) {
  const v = value ?? 0
  const r = 26
  const c = 2 * Math.PI * r
  const off = c * (1 - Math.max(0, Math.min(1, v)))
  const colorMap: Record<string, string> = {
    go: 'var(--go)', risk: 'var(--danger)', review: 'var(--review)', accent: 'var(--accent)',
  }
  const color = colorMap[tone] ?? 'var(--accent)'
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 64 64" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="32" cy="32" r={r} fill="none" stroke="var(--bg-2)" strokeWidth="7"/>
          <circle cx="32" cy="32" r={r} fill="none" stroke={color} strokeWidth="7"
            strokeLinecap="round" strokeDasharray={c} strokeDashoffset={off}
            style={{ transition: 'stroke-dashoffset .8s var(--ease)' }}/>
        </svg>
        <div style={{
          position: 'absolute', inset: 0, display: 'grid', placeItems: 'center',
          fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '.92rem', color: 'var(--ink)',
        }}>
          {v.toFixed(2)}
        </div>
      </div>
      <span className="field-label">{label}</span>
    </div>
  )
}

export function FitBar({ value }: { value: number | null }) {
  const v = value ?? 0
  const color = v >= 0.8 ? 'var(--go)' : v >= 0.65 ? 'var(--review)' : 'var(--skip)'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div className="bar" style={{ width: 56, flexShrink: 0 }}>
        <span style={{ width: `${v * 100}%`, background: color }} />
      </div>
      <span className="tnum" style={{ fontSize: '.8rem', color }}>{v.toFixed(2)}</span>
    </div>
  )
}

export function DeadlinePill({ deadline }: { deadline: string | null }) {
  if (!deadline) return <span style={{ color: 'var(--faint)' }}>—</span>
  const days = Math.ceil((new Date(deadline).getTime() - Date.now()) / 86400000)
  const color = days < 0 ? 'var(--danger)' : days <= 3 ? 'var(--review)' : 'var(--muted)'
  const label = days < 0 ? `${Math.abs(days)}d atrás` : days === 0 ? 'Hoje' : `${days}d`
  return <span className="tnum" style={{ fontSize: '.8rem', color }}>{label}</span>
}
