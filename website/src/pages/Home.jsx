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
          <h2 className="text-4xl font-bold mb-12 text-center">Why PromptyDumpty?</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon="🔄"
              title="Universal"
              description="One package works across multiple AI assistants. Write once, use everywhere."
            />
            <FeatureCard
              icon="📦"
              title="Simple"
              description="Just YAML and Git. No complex setup or dependencies required."
            />
            <FeatureCard
              icon="🎯"
              title="Auto-Detection"
              description="Detects your AI agent and installs files to the correct locations automatically."
            />
            <FeatureCard
              icon="🔒"
              title="Safe & Tracked"
              description="Clean installs and removals. Everything tracked in lockfiles."
            />
            <FeatureCard
              icon="🚀"
              title="Git-Based"
              description="Leverage Git for versioning, distribution, and collaboration."
            />
            <FeatureCard
              icon="📝"
              title="External References"
              description="Reference and curate content from any Git repository without forking."
            />
            <FeatureCard
              icon="🔧"
              title="Flexible Structure"
              description="Organize source files your way. Full control over installation paths."
            />
            <FeatureCard
              icon="🌐"
              title="Open Source"
              description="MIT licensed with community-driven development."
            />
          </div>
        </div>
      </section>

      {/* Supported Agents */}
      <section className="py-20 px-4 bg-slate-800/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold mb-12 text-center">Supported AI Coding Assistants</h2>
          <div className="flex flex-col items-center gap-1 max-w-4xl mx-auto">
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

function HexagonCard({ name, icon }) {
  return (
    <div className="relative w-32 h-28 group">
      {/* SVG Hexagon with border */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polygon 
          points="25,0 75,0 100,50 75,100 25,100 0,50" 
          className="fill-slate-800/50 stroke-slate-600 stroke-[3] group-hover:stroke-primary-500 group-hover:fill-slate-700/50 transition-all duration-300"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
      {/* Content */}
      <div className="relative h-full flex flex-col items-center justify-center gap-1">
        <div className="text-3xl">{icon}</div>
        <div className="text-xs font-medium text-center px-2">{name}</div>
      </div>
    </div>
  )
}

function BrickCard({ name, icon, empty }) {
  if (empty) {
    return (
      <div className="bg-slate-800/30 border-2 border-slate-700/50 rounded-sm px-6 py-4 w-44 h-16" 
           style={{
             boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.3), inset -2px -2px 4px rgba(255,255,255,0.05)'
           }}>
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
