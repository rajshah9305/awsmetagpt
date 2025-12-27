import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'

// Components
import Header from './components/Header'
import Footer from './components/Footer'

// Pages
import Home from './pages/Home'
import Generator from './pages/Generator'
import Results from './pages/Results'
import About from './pages/About'

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-secondary-50 to-primary-50">
      <Header />
      
      <main className="flex-1">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/generate" element={<Generator />} />
            <Route path="/results/:generationId" element={<Results />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </motion.div>
      </main>
      
      <Footer />
    </div>
  )
}

export default App