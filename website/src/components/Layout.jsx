import { Link, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <nav className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link to="/" className="flex items-center space-x-3">
              <div className="text-3xl">🥚</div>
              <span className="text-xl font-bold text-white">PromptyDumpty</span>
            </Link>
            <div className="flex space-x-8">
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
          </div>
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
              Visit us at{' '}
              <a href="https://dumpty.dev" className="text-primary-400 hover:text-primary-300">
                dumpty.dev
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
