import CodeBlock from '../components/CodeBlock'
import TerminalBlock from '../components/TerminalBlock'
import TableOfContents from '../components/TableOfContents'

const tocItems = [
  { id: 'command-reference', title: 'Command Reference' },
  { id: 'agent-detection', title: 'Agent Detection' },
  { id: 'agent-behaviors', title: 'Agent-Specific Behaviors' },
  { id: 'lockfile-format', title: 'Lockfile Format' },
  { id: 'package-organization', title: 'Package Organization' },
  { id: 'troubleshooting', title: 'Troubleshooting' },
  { id: 'contributing', title: 'Contributing' },
  { id: 'resources', title: 'Resources' },
]

export default function Documentation() {
  return (
    <div className="flex gap-8 max-w-7xl mx-auto px-4 py-12">
      <div className="flex-1 min-w-0 text-white">
        <h1 className="text-4xl font-bold mb-8">Documentation</h1>

        <section id="command-reference" className="mb-12 scroll-mt-24">
          <h2 className="text-3xl font-semibold mb-4">Command Reference</h2>
        
        <div className="space-y-6">
          <CommandDoc
            command="dumpty init"
            description="Initialize PromptyDumpty in your project. Detects your AI agent and creates necessary configuration."
            options={[
              { flag: "--agent", description: "Initialize for specific agent. Defaults to auto-detect." },
              { flag: "--project-root", description: "Project root directory. Defaults to git repository root or current directory." }
            ]}
            example="dumpty init"
          />

          <CommandDoc
            command="dumpty install PACKAGE_URL"
            description="Install a package from a Git repository. Use the full repository URL for installation."
            options={[
              { flag: "--agent", description: "Install for specific agent (copilot, claude, etc.)" },
              { flag: "--version", description: "Install specific version tag (e.g., 1.2.0 or v1.2.0)" },
              { flag: "--commit", description: "Install from specific commit hash (skips version validation)" },
              { flag: "--project-root", description: "Project root directory. Defaults to git repository root or current directory." }
            ]}
            example={`dumpty install https://github.com/org/my-prompts
dumpty install https://github.com/org/my-prompts --version 1.2.0
dumpty install https://github.com/org/my-prompts --commit abc123def
dumpty install https://github.com/org/my-prompts --agent copilot`}
          />

          <CommandDoc
            command="dumpty list"
            description="List all installed packages with their versions and installed files."
            options={[
              { flag: "--project-root", description: "Project root directory. Defaults to git repository root or current directory." }
            ]}
            example="dumpty list"
          />

          <CommandDoc
            command="dumpty show PACKAGE_NAME"
            description="Display detailed information about an installed package. Use the package name from the manifest (not the URL)."
            options={[
              { flag: "--project-root", description: "Project root directory. Defaults to git repository root or current directory." }
            ]}
            example="dumpty show my-prompts"
          />

          <CommandDoc
            command="dumpty update PACKAGE_NAME"
            description="Update a package to the latest version. Use the package name from the manifest (not the URL)."
            options={[
              { flag: "--all", description: "Update all installed packages" },
              { flag: "--version", description: "Update to specific version tag (e.g., 2.0.0 or v2.0.0)" },
              { flag: "--commit", description: "Update to specific commit hash (skips version validation)" },
              { flag: "--project-root", description: "Project root directory. Defaults to git repository root or current directory." }
            ]}
            example={`dumpty update my-prompts
dumpty update my-prompts --version 2.0.0
dumpty update my-prompts --commit abc123def
dumpty update --all`}
          />

          <CommandDoc
            command="dumpty uninstall PACKAGE_NAME"
            description="Remove a package and all its installed files. Use the package name from the manifest (not the URL)."
            options={[
              { flag: "--project-root", description: "Project root directory. Defaults to git repository root or current directory." }
            ]}
            example="dumpty uninstall my-prompts"
          />
        </div>
      </section>

      <section id="agent-detection" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Agent Detection</h2>
        <p className="text-slate-300 mb-4">
          PromptyDumpty automatically detects which AI coding assistants are configured in your project by looking for specific directories:
        </p>
        <div className="bg-slate-900/50 rounded-lg p-6 border border-slate-700">
          <table className="w-full text-slate-300">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-2 pr-4">Agent</th>
                <th className="text-left py-2">Detection Path</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-700/50">
                <td className="py-2 pr-4">GitHub Copilot</td>
                <td className="py-2"><code>.github/</code></td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2 pr-4">Claude</td>
                <td className="py-2"><code>.claude/</code></td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2 pr-4">Cursor</td>
                <td className="py-2"><code>.cursor/</code></td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2 pr-4">Gemini</td>
                <td className="py-2"><code>.gemini/</code></td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-2 pr-4">Windsurf</td>
                <td className="py-2"><code>.windsurf/</code></td>
              </tr>
              <tr>
                <td className="py-2 pr-4">Cline</td>
                <td className="py-2"><code>.cline/</code></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section id="agent-behaviors" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Agent-Specific Behaviors</h2>
        <p className="text-slate-300 mb-4">
          Some agents have additional behaviors when packages are installed or uninstalled:
        </p>
        <div className="space-y-4">
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 text-primary-400">GitHub Copilot</h3>
            <p className="text-slate-300 mb-3">
              Automatically updates VS Code workspace settings to register package directories for prompts and custom agents.
            </p>
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
              <p className="text-xs text-slate-400 mb-2">Updates <code>.vscode/settings.json</code>:</p>
              <CodeBlock language="json">
{`{
  "chat.promptFilesLocations": {
    ".github/prompts/my-package": true
  },
  "chat.agentFilesLocations": {
    ".github/agents/my-package": true
  }
}`}
              </CodeBlock>
            </div>
            <p className="text-slate-400 text-sm mt-3">
              This ensures GitHub Copilot can discover and use the installed prompts and custom agents. Both settings are automatically cleaned up on uninstall.
            </p>
          </div>
        </div>
      </section>

      <section id="lockfile-format" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Lockfile Format</h2>
        <p className="text-slate-300 mb-4">
          PromptyDumpty maintains a <code>dumpty.lock</code> file to track installed packages:
        </p>
        
        <h3 className="text-xl font-semibold mb-3">Standard Package</h3>
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="yaml">
{`version: 1.0
packages:
  - name: my-workflows
    version: 1.0.0
    source: https://github.com/org/my-workflows
    source_type: git
    resolved: https://github.com/org/my-workflows/commit/abc123def456
    installed_at: "2025-11-04T10:30:00Z"
    installed_for:
      - copilot
    files:
      copilot:
        - source: src/review.md
          installed: .github/prompts/my-workflows/review.prompt.md
          checksum: sha256:abc...
    manifest_checksum: sha256:manifest123...`}
          </CodeBlock>
        </div>

        <h3 className="text-xl font-semibold mb-3">Package with External Repository</h3>
        <div className="border border-slate-700 mb-4">
          <CodeBlock language="yaml">
{`version: 1.0
packages:
  - name: curated-prompts
    version: 1.0.0
    source: https://github.com/org/curated-prompts
    source_type: git
    resolved: https://github.com/org/curated-prompts/commit/def456
    external_repo:
      url: https://github.com/community/prompts
      commit: a1b2c3d4e5f6789012345678901234567890abcd
    installed_at: "2025-11-12T10:30:00Z"
    installed_for:
      - copilot
    files:
      copilot:
        - source: prompts/refactoring.md
          installed: .github/prompts/curated-prompts/refactoring.prompt.md
          checksum: sha256:xyz...`}
          </CodeBlock>
        </div>
        <p className="text-slate-300">
          This file ensures clean updates and removals, and helps track what's installed in your project. For packages with external repositories, both the manifest and external repository commits are tracked.
        </p>
      </section>

      <section id="package-organization" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Package Organization</h2>
        <p className="text-slate-300 mb-4">
          Packages are installed with artifact types in the path to organize files by their purpose:
        </p>
        <div className="border border-slate-700 mb-4">
          <CodeBlock language="bash">
{`.github/
├── prompts/
│   └── my-workflows/              # Package namespace
│       ├── review.prompt.md
│       └── planning.prompt.md
└── agents/
    └── my-workflows/              # Same package, different type
        └── standards.agent.md

.cursor/
└── rules/
    └── my-workflows/
        └── standards.md`}
          </CodeBlock>
        </div>
        <p className="text-slate-300 mb-3">
          Files are organized using the pattern: <code className="bg-slate-700 px-2 py-0.5 rounded text-sm">{`{agent_dir}/{type}/{package_name}/{file}`}</code>
        </p>
        <p className="text-slate-300">
          Each package gets its own subdirectory within the artifact type folder, making it easy to identify, organize, and remove packages cleanly.
        </p>
      </section>

      <section id="troubleshooting" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Troubleshooting</h2>

        <div className="space-y-6">
          <TroubleshootingItem
            question="Agent not detected?"
            answer="Make sure the appropriate directory exists (.github/, .claude/, etc.). Run `dumpty init` to set up the structure."
          />

          <TroubleshootingItem
            question="Package installation failed?"
            answer="Verify the repository URL is correct and accessible. Check that the package has a valid dumpty.package.yaml manifest."
          />

          <TroubleshootingItem
            question="Files not appearing?"
            answer="Ensure the file paths in the manifest match your package structure. Check that the installed paths are correct for your agent's directory."
          />

          <TroubleshootingItem
            question="Clean slate needed?"
            answer="You can manually delete the dumpty.lock file and installed package directories to start fresh."
          />
        </div>
      </section>

      <section id="contributing" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Contributing</h2>
        <p className="text-slate-300 mb-4">
          PromptyDumpty is open source and welcomes contributions!
        </p>
        <div className="bg-primary-900/30 border border-primary-700/50 rounded-lg p-6">
          <ul className="space-y-3 text-slate-300">
            <li>🐛 Report bugs on <a href="https://github.com/dasiths/PromptyDumpty/issues" className="text-primary-400 hover:text-primary-300" target="_blank" rel="noopener noreferrer">GitHub Issues</a></li>
            <li>💡 Suggest features or improvements</li>
            <li>🔧 Submit pull requests with fixes or enhancements</li>
            <li>📝 Improve documentation</li>
            <li>⭐ Star the repository if you find it useful</li>
          </ul>
        </div>
      </section>

      <section id="resources" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Resources</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <a 
            href="https://github.com/dasiths/PromptyDumpty" 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 hover:border-primary-600/50 transition-colors"
          >
            <h3 className="text-xl font-semibold mb-2">GitHub Repository</h3>
            <p className="text-slate-400">Source code, examples, and issue tracker</p>
          </a>
          
          <a 
            href="https://github.com/dasiths/PromptyDumpty/tree/main/examples" 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 hover:border-primary-600/50 transition-colors"
          >
            <h3 className="text-xl font-semibold mb-2">Example Packages</h3>
            <p className="text-slate-400">Sample packages to learn from</p>
          </a>
          
          <a 
            href="https://pypi.org/project/prompty-dumpty/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 hover:border-primary-600/50 transition-colors"
          >
            <h3 className="text-xl font-semibold mb-2">PyPI Package</h3>
            <p className="text-slate-400">Official Python package registry</p>
          </a>
          
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-semibold mb-2">License</h3>
            <p className="text-slate-400">MIT License - Free and open source</p>
          </div>
        </div>
      </section>
      </div>
      <TableOfContents items={tocItems} />
    </div>
  )
}

function CommandDoc({ command, description, options, example }) {
  return (
    <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
      <h3 className="text-xl font-semibold mb-2 text-primary-400">{command}</h3>
      <p className="text-slate-300 mb-4">{description}</p>
      
      {options && (
        <div className="mb-4">
          <p className="text-sm font-semibold text-slate-400 mb-2">Options:</p>
          <ul className="space-y-1 text-slate-300 text-sm">
            {options.map((opt, idx) => (
              <li key={idx}>
                <code className="text-primary-400">{opt.flag}</code> - {opt.description}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      <div>
        <p className="text-xs text-slate-400 mb-1">Example:</p>
        <TerminalBlock>{example}</TerminalBlock>
      </div>
    </div>
  )
}

function TroubleshootingItem({ question, answer }) {
  return (
    <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
      <h3 className="text-lg font-semibold mb-2 text-primary-400">{question}</h3>
      <p className="text-slate-300">{answer}</p>
    </div>
  )
}
