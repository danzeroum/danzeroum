import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Shell/Sidebar'
import { Topbar } from './components/Shell/Topbar'
import Dashboard from './screens/Dashboard'
import TenderList from './screens/TenderList'
import TenderDetail from './screens/TenderDetail'
import Collect from './screens/Collect'
import Config from './screens/Config'
import Documents from './screens/Documents'
import Certificates from './screens/Certificates'
import Proposals from './screens/Proposals'
import CRM from './screens/CRM'
import Calc from './screens/Calc'

function getInitialTheme(): boolean {
  const stored = localStorage.getItem('dz-theme')
  if (stored) return stored === 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export default function App() {
  const [dark, setDark] = useState(getInitialTheme)
  const [globalSearch, setGlobalSearch] = useState('')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('dz-theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <div className="app">
      <Sidebar dark={dark} />
      <main className="main">
        <Topbar dark={dark} onToggleTheme={() => setDark(d => !d)} onSearch={setGlobalSearch} />
        <div className="content scroll">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/oportunidades" element={<TenderList globalSearch={globalSearch} />} />
            <Route path="/oportunidades/:id" element={<TenderDetail />} />
            <Route path="/coleta" element={<Collect />} />
            <Route path="/config" element={<Config />} />
            <Route path="/documentos" element={<Documents />} />
            <Route path="/atestados" element={<Certificates />} />
            <Route path="/propostas" element={<Proposals />} />
            <Route path="/crm" element={<CRM />} />
            <Route path="/calculadora" element={<Calc />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}
