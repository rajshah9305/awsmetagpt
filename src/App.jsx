import React from 'react'
import { Routes, Route } from 'react-router-dom'

// Components
import Header from './components/Header'
import Footer from './components/Footer'

// Pages
import Home from './pages/Home'
import Generator from './pages/Generator'
import Results from './pages/Results'
import About from './pages/About'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('App error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center px-4 mesh-gradient">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 bg-error-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-error-600 text-2xl font-bold">!</span>
            </div>
            <h1 className="text-xl font-display font-bold text-neutral-900 mb-2">Something went wrong</h1>
            <p className="text-neutral-600 mb-6 text-sm">
              {this.state.error?.message || 'An unexpected error occurred.'}
            </p>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="btn-primary"
            >
              Try Again
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

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