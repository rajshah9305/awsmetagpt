import React from 'react'
import { Routes, Route } from 'react-router-dom'

// Components
import Header from './components/Header'
import Footer from './components/Footer'
import ErrorBoundary from './components/ErrorBoundary'

// Pages
import Home from './pages/Home'
import Generator from './pages/Generator'
import Results from './pages/Results'
import About from './pages/About'

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col">
        <Header />

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/generate" element={<Generator />} />
            <Route path="/results/:generationId" element={<Results />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </ErrorBoundary>
  )
}

export default App