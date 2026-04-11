import React from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'

import Header from './components/Header'
import Footer from './components/Footer'
import ErrorBoundary from './components/ErrorBoundary'

import Home from './pages/Home'
import Generator from './pages/Generator'
import Results from './pages/Results'
import About from './pages/About'

const PageWrapper = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 6 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.22, ease: 'easeOut' }}
  >
    {children}
  </motion.div>
)

function App() {
  const location = useLocation()

  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/"                        element={<PageWrapper><Home /></PageWrapper>} />
              <Route path="/generate"                element={<PageWrapper><Generator /></PageWrapper>} />
              <Route path="/results/:generationId"   element={<PageWrapper><Results /></PageWrapper>} />
              <Route path="/about"                   element={<PageWrapper><About /></PageWrapper>} />
            </Routes>
          </AnimatePresence>
        </main>
        <Footer />
      </div>
    </ErrorBoundary>
  )
}

export default App
