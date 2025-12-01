import { Link, Outlet } from 'react-router-dom'
import { useState } from 'react'
import { VERSION } from '../version'

export default function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <nav className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-20 items-center">
            <Link to="/" className="flex items-center space-x-3">
              <div className="text-3xl">🥚</div>
              <div className="flex flex-col">
                <span className="text-xl font-bold text-white">PromptyDumpty</span>
                <span className="text-xs text-slate-400">v{VERSION}</span>
              </div>
            </Link>            {/* Desktop Menu */}
            <div className="hidden md:flex space-x-8 items-center">
              <Link to="/" className="text-slate-300 hover:text-white transition-colors">
                Home
              </Link>
              <Link to="/getting-started" className="text-slate-300 hover:text-white transition-colors">
                Getting Started
              </Link>
              <Link to="/creating-packages" className="text-slate-300 hover:text-white transition-colors">
                Create Packages
              </Link>
              <Link to="/docs" className="text-slate-300 hover:text-white transition-colors">
                Docs
              </Link>
              <a 
                href="https://github.com/dasiths/PromptyDumpty" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-slate-300 hover:text-white transition-colors"
              >
                GitHub
              </a>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden text-slate-300 hover:text-white focus:outline-none"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              <svg className="h-6 w-6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                {mobileMenuOpen ? (
                  <path d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 space-y-3">
              <Link 
                to="/" 
                className="block text-slate-300 hover:text-white transition-colors py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Home
              </Link>
              <Link 
                to="/getting-started" 
                className="block text-slate-300 hover:text-white transition-colors py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Getting Started
              </Link>
              <Link 
                to="/creating-packages" 
                className="block text-slate-300 hover:text-white transition-colors py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Create Packages
              </Link>
              <Link 
                to="/docs" 
                className="block text-slate-300 hover:text-white transition-colors py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Docs
              </Link>
              <a 
                href="https://github.com/dasiths/PromptyDumpty" 
                target="_blank" 
                rel="noopener noreferrer"
                className="block text-slate-300 hover:text-white transition-colors py-2"
              >
                GitHub
              </a>
            </div>
          )}
        </div>
      </nav>
      <main>
        <Outlet />
      </main>
      <footer className="bg-slate-900/50 border-t border-slate-700/50 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-slate-400">
            <p>© 2025 PromptyDumpty. Licensed under MIT.</p>
            <p className="mt-2">
              <a href="https://github.com/dasiths/PromptyDumpty" className="text-primary-400 hover:text-primary-300">
                GitHub
              </a>
              {' • '}
              <a href="https://github.com/dasiths/PromptyDumpty/issues" className="text-primary-400 hover:text-primary-300">
                Submit Issues
              </a>
              {' • '}
              <a href="mailto:info@dumpty.dev" className="text-primary-400 hover:text-primary-300">
                Contact
              </a>
            </p>
            <p className="mt-2 text-sm">
              Developed using GitHub Copilot
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
