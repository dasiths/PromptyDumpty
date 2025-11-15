import { Link } from 'react-router-dom'
import TerminalBlock from '../components/TerminalBlock'

export default function Home() {
  return (
    <div className="text-white">
      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <img src="/logo.png" alt="PromptyDumpty Logo" className="w-48 h-48 mx-auto mb-6" />
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent min-h-[80px] flex items-center justify-center">
            PromptyDumpty
          </h1>
          <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto">
            A lightweight, universal package manager for AI coding assistants
          </p>
          <p className="text-lg text-slate-400 mb-12 max-w-2xl mx-auto">
            Install and manage prompts, instructions, rules, and workflows across GitHub Copilot, Claude, Cursor, Gemini, Windsurf, OpenCode, and more.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/getting-started"
              className="bg-primary-600 hover:bg-primary-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
            >
              Get Started
            </Link>
            <a
              href="https://github.com/dasiths/PromptyDumpty"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-slate-700 hover:bg-slate-600 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Quick Example */}
      <section className="py-16 px-4 bg-slate-800/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-8 text-center">Quick Start</h2>
          <TerminalBlock>
{`# Install PromptyDumpty
pip install prompty-dumpty

# Initialize in your project
dumpty init

# Install a package
dumpty install https://github.com/org/my-prompts

# List installed packages
dumpty list`}
          </TerminalBlock>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold mb-16 text-center">Why PromptyDumpty?</h2>
          
          {/* For Solo Developers */}
          <div className="mb-16">
            <h3 className="text-2xl font-semibold mb-6 text-center text-primary-400">For Solo Developers</h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              <FeatureCard
                icon="🎯"
                title="Zero Config"
                description="Auto-detects your AI agent. Just install and go—no setup required."
              />
              <FeatureCard
                icon="⚡"
                title="Lightning Fast"
                description="Simple CLI commands get you productive in seconds, not hours."
              />
              <FeatureCard
                icon="🔄"
                title="Switch Agents Freely"
                description="One package works everywhere. Try different AI tools without rewriting."
              />
            </div>
          </div>

          {/* For Teams */}
          <div className="mb-16">
            <h3 className="text-2xl font-semibold mb-6 text-center text-emerald-400">For Teams</h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              <FeatureCard
                icon="🔒"
                title="Version Control"
                description="Git-based packages mean everyone stays in sync with lockfiles."
              />
              <FeatureCard
                icon="👥"
                title="Share Standards"
                description="Distribute team prompts, rules, and workflows as versioned packages."
              />
              <FeatureCard
                icon="📊"
                title="Track Everything"
                description="Know exactly what's installed, from where, and when it changed."
              />
            </div>
          </div>

          {/* For Open Source */}
          <div>
            <h3 className="text-2xl font-semibold mb-6 text-center text-blue-400">For Open Source</h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              <FeatureCard
                icon="🌐"
                title="Publish Anywhere"
                description="Host packages on GitHub, GitLab, or any Git repository."
              />
              <FeatureCard
                icon="📝"
                title="Curate Without Forking"
                description="Reference external repos to build collections without duplication."
              />
              <FeatureCard
                icon="🎁"
                title="MIT Licensed"
                description="Free and open source. Build on it, extend it, make it yours."
              />
            </div>
          </div>
        </div>
      </section>

      {/* Supported Agents */}
      <section className="py-20 px-4 bg-slate-800/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold mb-12 text-center">Supported AI Coding Assistants</h2>
          
          {/* Mobile: Simple grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 md:hidden max-w-2xl mx-auto">
            <BrickCard name="GitHub Copilot" icon="💻" mobile />
            <BrickCard name="Claude" icon="🤖" mobile />
            <BrickCard name="Cursor" icon="⚡" mobile />
            <BrickCard name="Gemini" icon="✨" mobile />
            <BrickCard name="Windsurf" icon="🏄" mobile />
            <BrickCard name="Cline" icon="🔮" mobile />
            <BrickCard name="Aider" icon="🔧" mobile />
            <BrickCard name="Continue" icon="➡️" mobile />
            <BrickCard name="OpenCode" icon="🔓" mobile />
          </div>
          
          {/* Desktop: Brick wall */}
          <div className="hidden md:flex flex-col items-center gap-1 max-w-4xl mx-auto">
            {/* Row 1 - 4 bricks */}
            <div className="flex gap-1">
              <BrickCard name="GitHub Copilot" icon="💻" />
              <BrickCard name="Claude" icon="🤖" />
              <BrickCard name="Cursor" icon="⚡" />
              <BrickCard empty />
            </div>
            
            {/* Row 2 - 4 bricks (offset) */}
            <div className="flex gap-1 -ml-24">
              <BrickCard empty />
              <BrickCard name="Gemini" icon="✨" />
              <BrickCard name="Windsurf" icon="🏄" />
              <BrickCard name="Cline" icon="🔮" />
              <BrickCard empty />
            </div>
            
            {/* Row 3 - 4 bricks */}
            <div className="flex gap-1">
              <BrickCard name="Aider" icon="🔧" />
              <BrickCard name="Continue" icon="➡️" />
              <BrickCard name="OpenCode" icon="🔓" />
              <BrickCard empty />
            </div>
            
            {/* Row 4 - 4 bricks (offset) */}
            <div className="flex gap-1 -ml-24">
              <BrickCard empty />
              <BrickCard empty />
              <BrickCard empty />
              <BrickCard empty />
              <BrickCard empty />
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to get started?</h2>
          <p className="text-xl text-slate-300 mb-8">
            Install PromptyDumpty and start managing your AI coding assistants today.
          </p>
          <Link
            to="/getting-started"
            className="inline-block bg-primary-600 hover:bg-primary-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
          >
            Get Started Now
          </Link>
        </div>
      </section>
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 hover:border-primary-600/50 transition-colors">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-slate-400">{description}</p>
    </div>
  )
}

function AgentCard({ name, icon }) {
  return (
    <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 text-center hover:border-primary-600/50 transition-colors">
      <div className="text-4xl mb-2">{icon}</div>
      <div className="text-sm font-medium">{name}</div>
    </div>
  )
}

function BrickCard({ name, icon, empty, mobile }) {
  if (empty) {
    return (
      <div className="bg-slate-800/30 border-2 border-slate-700/50 rounded-sm px-6 py-4 w-44 h-16" 
           style={{
             boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.3), inset -2px -2px 4px rgba(255,255,255,0.05)'
           }}>
      </div>
    )
  }
  
  if (mobile) {
    return (
      <div className="bg-gradient-to-br from-slate-700/90 to-slate-800/90 border-2 border-slate-600 rounded-sm px-3 py-3 hover:border-primary-500 hover:from-slate-600/90 hover:to-slate-700/90 transition-all duration-300 group relative"
           style={{
             boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.4), inset -2px -2px 4px rgba(255,255,255,0.08), 2px 2px 6px rgba(0,0,0,0.3)'
           }}>
        <div className="flex flex-col items-center gap-2 text-center">
          <div className="text-2xl">{icon}</div>
          <div className="text-xs font-semibold leading-tight">{name}</div>
        </div>
        {/* Brick texture lines */}
        <div className="absolute inset-0 pointer-events-none opacity-20">
          <div className="absolute top-1/3 left-0 right-0 h-px bg-slate-900"></div>
          <div className="absolute top-2/3 left-0 right-0 h-px bg-slate-900"></div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-gradient-to-br from-slate-700/90 to-slate-800/90 border-2 border-slate-600 rounded-sm px-6 py-4 w-44 h-16 hover:border-primary-500 hover:from-slate-600/90 hover:to-slate-700/90 transition-all duration-300 group relative"
         style={{
           boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.4), inset -2px -2px 4px rgba(255,255,255,0.08), 2px 2px 6px rgba(0,0,0,0.3)'
         }}>
      <div className="flex items-center gap-3 h-full">
        <div className="text-2xl">{icon}</div>
        <div className="text-sm font-semibold">{name}</div>
      </div>
      {/* Brick texture lines */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <div className="absolute top-1/3 left-0 right-0 h-px bg-slate-900"></div>
        <div className="absolute top-2/3 left-0 right-0 h-px bg-slate-900"></div>
      </div>
    </div>
  )
}
