import TerminalBlock from '../components/TerminalBlock'
import TableOfContents from '../components/TableOfContents'

const tocItems = [
  { id: 'installation', title: 'Installation' },
  { id: 'initialize', title: 'Initialize Your Project' },
  { id: 'installing-packages', title: 'Installing Packages' },
  { id: 'managing-packages', title: 'Managing Packages' },
  { id: 'how-it-works', title: 'How It Works' },
  { id: 'next-steps', title: 'Next Steps' },
]

export default function GettingStarted() {
  return (
    <div className="flex gap-8 max-w-7xl mx-auto px-4 py-12">
      <div className="flex-1 min-w-0 text-white">
        <h1 className="text-4xl font-bold mb-8">Getting Started</h1>

        <section id="installation" className="mb-12 scroll-mt-24">
          <h2 className="text-3xl font-semibold mb-4">Installation</h2>
        <p className="text-slate-300 mb-4">
          Install PromptyDumpty using pip:
        </p>
        <div className="mb-6">
          <TerminalBlock>pip install prompty-dumpty</TerminalBlock>
        </div>
        <p className="text-slate-300 mb-4">
          Or install from source:
        </p>
        <TerminalBlock>
{`git clone https://github.com/dasiths/PromptyDumpty.git
cd PromptyDumpty
pip install -e .`}
        </TerminalBlock>
      </section>

      <section id="initialize" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Initialize Your Project</h2>
        <p className="text-slate-300 mb-4">
          Navigate to your project directory and initialize PromptyDumpty:
        </p>
        <div className="mb-6">
          <TerminalBlock>
{`cd your-project
dumpty init`}
          </TerminalBlock>
        </div>
        <p className="text-slate-300">
          This will detect your AI agent and set up the necessary configuration files.
        </p>
      </section>

      <section id="installing-packages" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Installing Packages</h2>
        <p className="text-slate-300 mb-4">
          Install a package from a Git repository using the full URL:
        </p>
        <div className="mb-6">
          <TerminalBlock>dumpty install https://github.com/org/my-prompts</TerminalBlock>
        </div>
        <p className="text-slate-300 mb-4">
          Install a specific version tag:
        </p>
        <div className="mb-6">
          <TerminalBlock>dumpty install https://github.com/org/my-prompts --version 1.2.0</TerminalBlock>
        </div>
        <p className="text-slate-300 mb-4">
          Install for a specific agent:
        </p>
        <div className="mb-6">
          <TerminalBlock>dumpty install https://github.com/org/my-prompts --agent copilot</TerminalBlock>
        </div>
        <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
          <p className="text-blue-200 text-sm">
            <strong>Note:</strong> After installation, use the package name from the manifest (e.g., <code>my-prompts</code>) for managing the package with <code>update</code>, <code>uninstall</code>, and <code>show</code> commands.
          </p>
        </div>
      </section>

      <section id="managing-packages" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Managing Packages</h2>
        <p className="text-slate-300 mb-6">
          After installation, manage packages using their name from the manifest (not the full URL).
        </p>
        
        <h3 className="text-2xl font-semibold mb-3 mt-6">List Installed Packages</h3>
        <div className="mb-6">
          <TerminalBlock>dumpty list</TerminalBlock>
        </div>

        <h3 className="text-2xl font-semibold mb-3">Update Packages</h3>
        <p className="text-slate-300 mb-3 text-sm">
          Use the package name from the manifest:
        </p>
        <div className="mb-6">
          <TerminalBlock>
{`# Update a specific package by name
dumpty update my-prompts

# Update all packages
dumpty update --all`}
          </TerminalBlock>
        </div>

        <h3 className="text-2xl font-semibold mb-3">Uninstall Packages</h3>
        <p className="text-slate-300 mb-3 text-sm">
          Use the package name from the manifest:
        </p>
        <div className="mb-6">
          <TerminalBlock>dumpty uninstall my-prompts</TerminalBlock>
        </div>

        <h3 className="text-2xl font-semibold mb-3">Show Package Info</h3>
        <p className="text-slate-300 mb-3 text-sm">
          View details about an installed package:
        </p>
        <TerminalBlock>dumpty show my-prompts</TerminalBlock>
      </section>

      <section id="how-it-works" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">How It Works</h2>
        <div className="space-y-4 text-slate-300">
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-3xl mr-4">1️⃣</div>
              <div>
                <h4 className="text-xl font-semibold text-white mb-2">Auto-Detection</h4>
                <p>PromptyDumpty scans your project for AI agent configuration files and directories (like <code>.github/prompts/</code>, <code>.claude/commands/</code>, etc.).</p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-3xl mr-4">2️⃣</div>
              <div>
                <h4 className="text-xl font-semibold text-white mb-2">Smart Installation</h4>
                <p>Packages are installed to the correct directories for your detected agent, with files organized by package name for easy management.</p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-3xl mr-4">3️⃣</div>
              <div>
                <h4 className="text-xl font-semibold text-white mb-2">Lockfile Tracking</h4>
                <p>All installations are tracked in a <code>dumpty.lock</code> file, ensuring clean updates and removals.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="next-steps" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Next Steps</h2>
        <div className="bg-primary-900/30 border border-primary-700/50 rounded-lg p-6">
          <ul className="space-y-3 text-slate-300">
            <li>✅ Check out <a href="/creating-packages" className="text-primary-400 hover:text-primary-300">Creating Packages</a> to learn how to create your own packages</li>
            <li>✅ Read the <a href="/docs" className="text-primary-400 hover:text-primary-300">full documentation</a> for advanced features</li>
            <li>✅ Explore <a href="https://github.com/dasiths/PromptyDumpty/tree/main/examples" className="text-primary-400 hover:text-primary-300" target="_blank" rel="noopener noreferrer">example packages</a> on GitHub</li>
          </ul>
        </div>
      </section>
      </div>
      <TableOfContents items={tocItems} />
    </div>
  )
}
