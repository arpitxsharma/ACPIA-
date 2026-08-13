import { useState } from 'react'
import './styles/variables.css'
import './styles/layout.css'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import CaseView from './pages/CaseView'

// We're not using React Router for this project - it's a single flow
// (landing -> dashboard -> case view) so plain state switching keeps
// the stack smaller and easier to explain to judges.
function App() {
  const [currentView, setCurrentView] = useState('landing')

  return (
    <div className="app">
      {currentView === 'landing' && (
        <Landing onEnter={() => setCurrentView('dashboard')} />
      )}

      {currentView === 'dashboard' && (
        <Dashboard
          onSelectCase={() => {
            // We only have one demo case for the PoC, so any case click
            // opens it. Real per-case routing would come with a backend
            // case list, but that's beyond what the demo needs.
            setCurrentView('case')
          }}
        />
      )}

      {currentView === 'case' && (
        <CaseView onBack={() => setCurrentView('dashboard')} />
      )}
    </div>
  )
}

export default App
