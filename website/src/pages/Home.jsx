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
            Install and manage prompts, instructions, rules, and workflows across GitHub Copilot, Claude, Cursor, Gemini, Windsurf, and more.
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
              description="One package works across multiple AI coding assistants. No more maintaining separate versions."
            />
            <FeatureCard
              icon="📦"
              title="Simple"
              description="Just YAML files and Git repos. No complex infrastructure or dependencies."
            />
            <FeatureCard
              icon="🎯"
              title="Smart Detection"
              description="Automatically detects your AI agent and installs files to the right locations."
            />
            <FeatureCard
              icon="🔒"
              title="Safe"
              description="Clean installation and removal with full tracking via lockfiles."
            />
            <FeatureCard
              icon="🚀"
              title="Easy Sharing"
              description="Package and distribute your team's prompts with simple Git workflows."
            />
            <FeatureCard
              icon="🔧"
              title="Flexible"
              description="Organize your package files however you want. Full control over installed paths."
            />
            <FeatureCard
              icon="📝"
              title="Well Documented"
              description="Clear documentation and examples to get you started quickly."
            />
            <FeatureCard
              icon="🌐"
              title="Open Source"
              description="MIT licensed. Community-driven development on GitHub."
            />
          </div>
        </div>
      </section>

      {/* Supported Agents */}
      <section className="py-20 px-4 bg-slate-800/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold mb-12 text-center">Supported AI Coding Assistants</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            <AgentCard name="GitHub Copilot" icon="💻" />
            <AgentCard name="Claude" icon="🤖" />
            <AgentCard name="Cursor" icon="⚡" />
            <AgentCard name="Gemini" icon="✨" />
            <AgentCard name="Windsurf" icon="🏄" />
            <AgentCard name="Cline" icon="🔮" />
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
