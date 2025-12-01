import { Link } from 'react-router-dom'
import TerminalBlock from '../components/TerminalBlock'

export default function Home() {
  return (
    <div className="text-white">
      {/* Hero Section */}
      <section className="py-12 px-4">
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
      <section className="py-12 px-4 bg-slate-800/30">
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

      {/* The Problem Section */}
      <section className="py-12 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold mb-4 text-center">
            How PromptyDumpty Solves Your Problems
          </h2>
          <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
            Stop wrestling with manual prompt management. Here's what changes when you use PromptyDumpty.
          </p>
          
          <div className="space-y-6">
            <ProblemSolutionCard
              problem="Manual copying"
              problemDesc="Copying .md files between projects and AI agent folders"
              solution="One-command install"
              solutionDesc="dumpty install https://repo-url installs everything"
            />
            <ProblemSolutionCard
              problem="No updates"
              problemDesc="When prompts improve, you manually re-copy everywhere"
              solution="Version control"
              solutionDesc="dumpty update pulls latest versions automatically"
            />
            <ProblemSolutionCard
              problem="Messy removal"
              problemDesc="Deleting prompts leaves orphaned files scattered around"
              solution="Clean uninstall"
              solutionDesc="dumpty uninstall removes all files tracked in lockfile"
            />
            <ProblemSolutionCard
              problem="No tracking"
              problemDesc="Can't remember what's installed or where it came from"
              solution="Full audit trail"
              solutionDesc="Lockfile tracks every package, version, and file location"
            />
            <ProblemSolutionCard
              problem="Multi-tool duplication"
              problemDesc="Maintaining separate prompt versions for each AI assistant"
              solution="Universal packages"
              solutionDesc="One package manifest supports all AI assistants"
            />
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-12 px-4 bg-slate-800/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold mb-8 text-center">Features</h2>
          
          {/* For Package Consumers */}
          <div className="mb-16">
            <h3 className="text-2xl font-semibold mb-6 text-center text-primary-400">For Package Consumers</h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              <FeatureCard
                icon="🚀"
                title="One Command Install"
                description="No manual file copying. Point to a repo and everything installs automatically."
              />
              <FeatureCard
                icon="🔍"
                title="Smart Detection"
                description="Finds your AI agents and installs the right assets for each one automatically."
              />
              <FeatureCard
                icon="🔄"
                title="Easy Updates"
                description="Get latest versions with one command. No re-downloading or re-copying files."
              />
              <FeatureCard
                icon="📦"
                title="Discover Packages"
                description="Find and install community packages for your AI assistant instantly."
              />
              <FeatureCard
                icon="🔒"
                title="Reproducible Setup"
                description="Lockfile ensures everyone on your team has the exact same configuration."
              />
              <FeatureCard
                icon="✨"
                title="Just Works"
                description="Install packages and start using them immediately - no config needed."
              />
            </div>
          </div>

          {/* For Package Creators */}
          <div>
            <h3 className="text-2xl font-semibold mb-6 text-center text-emerald-400">For Package Creators</h3>
            <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              <FeatureCard
                icon="📇"
                title="Index Your Repo"
                description="Create a manifest to index prompts, scripts, configs, and docs already in your repository."
              />
              <FeatureCard
                icon="🎯"
                title="Multi-Agent Support"
                description="One manifest supports multiple AI assistants. Define agent-specific assets in the same package."
              />
              <FeatureCard
                icon="📦"
                title="Any Asset Type"
                description="Package prompts, rules, commands, scripts, configs, docs - anything users need to install."
              />
              <FeatureCard
                icon="🌐"
                title="Git-Based Distribution"
                description="Host on GitHub, GitLab, or any Git repository. No central registry or special hosting needed."
              />
              <FeatureCard
                icon="🔖"
                title="Git Tag Versioning"
                description="Version using Git tags. Users can install specific versions or automatically get the latest."
              />
              <FeatureCard
                icon="📝"
                title="Reference External Repos"
                description="Build curated collections by referencing files from other repositories without forking."
              />
            </div>
          </div>
        </div>
      </section>

      {/* Supported Agents */}
      <section className="py-12 px-4">
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
      <section className="py-12 px-4">
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

function ProblemSolutionCard({ problem, problemDesc, solution, solutionDesc }) {
  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
      <div className="grid md:grid-cols-[1fr_auto_1fr] gap-0">
        {/* Problem - Red side */}
        <div className="bg-red-900/10 p-6 text-right border-r border-slate-700/50">
          <h3 className="text-lg font-semibold text-red-400 mb-2">❌ {problem}</h3>
          <p className="text-slate-400 text-sm">{problemDesc}</p>
        </div>
        
        {/* Arrow - Centered */}
        <div className="hidden md:flex items-center justify-center px-4 bg-slate-800/80">
          <div className="text-4xl text-primary-400 font-bold">→</div>
        </div>
        
        {/* Solution - Green side */}
        <div className="bg-emerald-900/10 p-6 border-l border-slate-700/50 md:border-l-0">
          <h3 className="text-lg font-semibold text-emerald-400 mb-2">✅ {solution}</h3>
          <p className="text-slate-300 text-sm">{solutionDesc}</p>
        </div>
      </div>
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
