import CodeBlock from '../components/CodeBlock'
import TableOfContents from '../components/TableOfContents'

const tocItems = [
  { id: 'package-structure', title: 'Package Structure' },
  { id: 'manifest-file', title: 'The Manifest File' },
  { id: 'manifest-fields', title: 'Manifest Fields' },
  { id: 'artifact-categories', title: 'Artifact Categories' },
  { id: 'external-repos', title: 'External Repository References' },
  { id: 'example-package', title: 'Complete Example' },
  { id: 'supported-agents', title: 'Agent-Specific Artifact Types' },
  { id: 'publishing', title: 'Publishing Your Package' },
  { id: 'best-practices', title: 'Best Practices' },
]

export default function CreatingPackages() {
  return (
    <div className="flex gap-8 max-w-7xl mx-auto px-4 py-12">
      <div className="flex-1 min-w-0 text-white">
        <h1 className="text-4xl font-bold mb-8">Creating Packages</h1>

        <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-6 mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-blue-300">Why Create Packages?</h2>
          <p className="text-slate-300 mb-4">
            Turn your existing repository into a distributable package. Create a manifest to index your prompts, 
            scripts, configs, and other assets - then let consumers install them with one command.
          </p>
          <div className="space-y-3 text-slate-300">
            <div className="flex items-start gap-3">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>Index existing repo assets (prompts, scripts, configs, docs)</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>Support multiple AI assistants from a single manifest</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>Version your assets using Git tags</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="text-emerald-400 font-bold">✓</span>
              <span>Let consumers discover and install your work instantly</span>
            </div>
          </div>
        </div>

        <section id="package-structure" className="mb-12 scroll-mt-24">
          <h2 className="text-3xl font-semibold mb-4">
            <a href="#package-structure" className="hover:text-primary-400 transition-colors">Package Structure</a>
          </h2>
        <p className="text-slate-300 mb-4">
          A PromptyDumpty package is simply a Git repository with a <code>dumpty.package.yaml</code> manifest file that indexes your assets. 
          Keep your existing file structure - the manifest tells Dumpty what to install and where.
        </p>
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="bash">
{`my-package/
├── dumpty.package.yaml  # Package manifest
├── README.md
└── src/                 # Any structure you prefer
    ├── planning.md
    ├── review.md
    └── standards.md`}
          </CodeBlock>
        </div>
      </section>

      <section id="manifest-file" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">
          <a href="#manifest-file" className="hover:text-primary-400 transition-colors">The Manifest File</a>
        </h2>
        <p className="text-slate-300 mb-4">
          The <code>dumpty.package.yaml</code> manifest indexes your repository's assets and defines what gets installed for each AI agent. 
          Organize files by type (prompts, agents, rules, commands) or use the generic <code>files</code> type for scripts, configs, and other assets.
        </p>
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="yaml">
{`name: my-workflows
version: 1.0.0
description: Custom development workflows
manifest_version: 1.0
license: MIT
author: Your Name
homepage: https://github.com/org/my-workflows

agents:
  copilot:
    prompts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: code-review.prompt.md
    agents:
      - name: standards
        description: Coding standards agent
        file: src/standards.md
        installed_path: standards.agent.md

  claude:
    commands:
      - name: code-review
        description: Code review command
        file: src/review.md
        installed_path: review.md`}
          </CodeBlock>
        </div>
      </section>

      <section id="manifest-fields" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">
          <a href="#manifest-fields" className="hover:text-primary-400 transition-colors">Manifest Fields</a>
        </h2>
        
        <div className="space-y-6">
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-semibold mb-2">Package Metadata</h3>
            <ul className="space-y-2 text-slate-300">
              <li><code className="text-primary-400">name</code> - Package name (required)</li>
              <li><code className="text-primary-400">version</code> - Semantic version (required)</li>
              <li><code className="text-primary-400">description</code> - Brief description (required)</li>
              <li><code className="text-primary-400">manifest_version</code> - Manifest format version, must be 1.0 (required)</li>
              <li><code className="text-primary-400">author</code> - Package author (optional)</li>
              <li><code className="text-primary-400">license</code> - Package license (optional)</li>
              <li><code className="text-primary-400">repository</code> - Git repository URL (optional)</li>
            </ul>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-semibold mb-2">Agent Configuration</h3>
            <p className="text-slate-300 mb-4">
              Each agent key (<code>copilot</code>, <code>claude</code>, <code>cursor</code>, etc.) contains artifact types that organize files into appropriate folders.
            </p>
            
            <h4 className="text-lg font-semibold mb-2 text-slate-200">Artifact Fields</h4>
            <ul className="space-y-2 text-slate-300 mb-4">
              <li><code className="text-primary-400">name</code> - Artifact identifier</li>
              <li><code className="text-primary-400">description</code> - What this artifact does</li>
              <li><code className="text-primary-400">file</code> - Source file path in your package</li>
              <li><code className="text-primary-400">installed_path</code> - Where to install relative to the type folder</li>
            </ul>
            
            <div className="bg-slate-900/50 rounded p-3 border border-slate-600">
              <p className="text-slate-400 text-sm mb-2">
                <strong>Installation path pattern:</strong>
              </p>
              <p className="text-slate-400 text-sm">
                <code className="text-primary-300">{`{agent_dir}/{type}/{package_name}/{installed_path}`}</code>
              </p>
              <p className="text-slate-500 text-xs mt-2">
                Example: <code>.github/prompts/my-package/review.prompt.md</code>
              </p>
            </div>
            
            <p className="text-slate-400 text-sm mt-4">
              See the <a href="#supported-agents" className="text-primary-400 hover:text-primary-300 underline">Agent-Specific Artifact Types</a> section for supported types per agent.
            </p>
          </div>
        </div>
      </section>

      <section id="artifact-categories" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">
          <a href="#artifact-categories" className="hover:text-primary-400 transition-colors">Artifact Categories</a>
        </h2>
        
        <p className="text-slate-300 mb-4">
          Categories allow users to selectively install artifacts from your package based on their workflow needs. For example, you might have development tools, testing tools, and documentation generators in one package.
        </p>

        <h3 className="text-xl font-semibold mb-3">Defining Categories</h3>
        <p className="text-slate-300 mb-4">
          Add a <code className="bg-slate-700 px-1.5 py-0.5 rounded">categories</code> section to your manifest:
        </p>
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="yaml">
{`name: dev-tools
version: 1.0.0
manifest_version: 1.0

categories:
  - name: development
    description: Tools for active development work
  - name: testing
    description: Testing and quality assurance prompts
  - name: documentation
    description: Documentation generation tools

agents:
  copilot:
    prompts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: code-review.prompt.md
        categories: [development]
      
      - name: test-generator
        description: Test generation prompt
        file: src/test-gen.md
        installed_path: test-gen.prompt.md
        categories: [testing]
      
      - name: multi-tool
        description: Multi-purpose development tool
        file: src/multi.md
        installed_path: multi-tool.prompt.md
        categories: [development, testing]
      
      - name: standards
        description: Universal coding standards
        file: src/standards.md
        installed_path: standards.prompt.md
        # No categories = universal (always installed)`}
          </CodeBlock>
        </div>

        <h3 className="text-xl font-semibold mb-3">Category Rules</h3>
        <div className="space-y-4">
          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h4 className="text-lg font-semibold mb-2 text-slate-200">Category Names</h4>
            <p className="text-slate-300 text-sm mb-2">
              Must match pattern: <code className="bg-slate-700 px-1.5 py-0.5 rounded text-primary-300">^[a-z0-9-]+$</code>
            </p>
            <p className="text-slate-400 text-sm">
              ✅ Valid: <code className="text-slate-300">development</code>, <code className="text-slate-300">code-review</code>, <code className="text-slate-300">testing123</code><br />
              ❌ Invalid: <code className="text-slate-300">Code Review</code>, <code className="text-slate-300">dev_tools</code>, <code className="text-slate-300">TESTING</code>
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h4 className="text-lg font-semibold mb-2 text-slate-200">Universal Artifacts</h4>
            <p className="text-slate-300 text-sm">
              Artifacts without categories are <strong>always installed</strong>, regardless of user selection. Use this for essential files everyone needs (like coding standards or general guidelines).
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h4 className="text-lg font-semibold mb-2 text-slate-200">Multi-Category Artifacts</h4>
            <p className="text-slate-300 text-sm">
              Artifacts can belong to multiple categories. They'll be installed if the user selects <strong>any</strong> of those categories.
            </p>
          </div>
        </div>

        <h3 className="text-xl font-semibold mb-3 mt-6">User Experience</h3>
        <p className="text-slate-300 mb-4">
          When users install a categorized package, they'll be prompted:
        </p>
        <div className="border border-slate-700 mb-4">
          <CodeBlock language="bash">
{`$ dumpty install https://github.com/org/dev-tools

Install all categories? [Y/n]: n

Select categories to install:
  1. development - Tools for active development work
  2. testing - Testing and quality assurance prompts
  3. documentation - Documentation generation tools

Enter category numbers (comma-separated): 1,2`}
          </CodeBlock>
        </div>

        <h3 className="text-xl font-semibold mb-3">CLI Flags</h3>
        <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
          <ul className="space-y-2 text-slate-300 text-sm">
            <li>
              <code className="bg-slate-700 px-1.5 py-0.5 rounded text-primary-300">--all-categories</code> - Skip prompts, install all categories
            </li>
            <li>
              <code className="bg-slate-700 px-1.5 py-0.5 rounded text-primary-300">--categories dev,test</code> - Install specific categories without prompts
            </li>
          </ul>
        </div>

        <h3 className="text-xl font-semibold mb-3 mt-6">Best Practices</h3>
        <div className="bg-primary-900/30 border border-primary-700/50 rounded-lg p-5">
          <ul className="space-y-2 text-slate-300 text-sm">
            <li>✅ Keep it simple: 2-5 categories per package</li>
            <li>✅ Use descriptive category names: <code className="text-slate-300">development</code> not <code className="text-slate-300">group1</code></li>
            <li>✅ Leave universal artifacts untagged (no categories field)</li>
            <li>✅ Multi-category sparingly - only for truly cross-cutting artifacts</li>
            <li>✅ Validate with <code className="text-primary-300">dumpty validate-manifest</code></li>
          </ul>
        </div>
      </section>

      <section id="external-repos" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">
          <a href="#external-repos" className="hover:text-primary-400 transition-colors">External Repository References</a>
        </h2>
        
        <p className="text-slate-300 mb-4">
          Create "wrapper packages" that reference files from repositories you don't own. Perfect for curating content from large community repositories or version-locking third-party prompts.
        </p>

        <h3 className="text-xl font-semibold mb-3">How It Works</h3>
        <p className="text-slate-300 mb-4">
          Add <code className="bg-slate-700 px-1.5 py-0.5 rounded">external_repository</code> to your manifest:
        </p>
        
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="yaml">
{`name: curated-prompts
version: 1.0.0
manifest_version: 1.0
author: Your Name
license: MIT
external_repository: https://github.com/community/prompts@a1b2c3d4e5f6789012345678901234567890abcd

agents:
  copilot:
    prompts:
      - name: refactoring
        file: prompts/refactoring.md
        installed_path: refactoring.prompt.md`}
          </CodeBlock>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 mb-6">
          <h4 className="text-lg font-semibold mb-2">Format</h4>
          <p className="text-slate-300 mb-3">
            <code className="bg-slate-700 px-1.5 py-0.5 rounded text-primary-300">&lt;git-url&gt;@&lt;40-char-commit-hash&gt;</code>
          </p>
          <ul className="space-y-2 text-slate-300 text-sm">
            <li>✅ Must use full 40-character commit hash</li>
            <li>✅ All file paths resolve from external repo</li>
            <li>✅ Both repos tracked in lockfile</li>
            <li>❌ No tags or branches (commits only)</li>
          </ul>
        </div>

        <h3 className="text-xl font-semibold mb-3">Use Cases</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-300 text-sm">
              <strong className="text-white">Curate Collections</strong><br />
              Select specific prompts from large community repos
            </p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-300 text-sm">
              <strong className="text-white">Version Lock</strong><br />
              Pin third-party content to specific commits
            </p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-300 text-sm">
              <strong className="text-white">Team Views</strong><br />
              Create team-specific views of shared content
            </p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-300 text-sm">
              <strong className="text-white">Lightweight</strong><br />
              Your repo only contains the manifest
            </p>
          </div>
        </div>
      </section>

      <section id="example-package" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">
          <a href="#example-package" className="hover:text-primary-400 transition-colors">Complete Example</a>
        </h2>
        <p className="text-slate-300 mb-4">
          Here's a complete example of a code review workflow package with categories:
        </p>
        
        <h3 className="text-xl font-semibold mb-3">Directory Structure</h3>
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="bash">
{`code-review-workflow/
├── dumpty.package.yaml
├── README.md
└── src/                     # Organize however you want!
    ├── review-checklist.md
    ├── security-audit.md
    ├── performance-tips.md
    └── coding-standards.md`}
          </CodeBlock>
        </div>

        <h3 className="text-xl font-semibold mb-3">Manifest</h3>
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="yaml">
{`name: code-review-workflow
version: 1.0.0
description: Comprehensive code review prompts
manifest_version: 1.0
license: MIT
author: Development Team
homepage: https://github.com/org/code-review-workflow

categories:
  - name: security
    description: Security review and audit tools
  - name: performance
    description: Performance optimization workflows
  - name: quality
    description: Code quality and review standards

agents:
  copilot:
    prompts:
      - name: review-checklist
        description: Code review checklist
        file: src/review-checklist.md
        installed_path: review.prompt.md
        categories: [quality]
      
      - name: security-audit
        description: Security review guidelines
        file: src/security-audit.md
        installed_path: security.prompt.md
        categories: [security]
      
      - name: performance-tips
        description: Performance optimization guide
        file: src/performance-tips.md
        installed_path: performance.prompt.md
        categories: [performance]
      
      - name: coding-standards
        description: Universal coding standards (always installed)
        file: src/coding-standards.md
        installed_path: standards.prompt.md
        # No categories = universal (always installed)
    agents:
      - name: review-mode
        description: Code review assistant agent
        file: src/review-checklist.md
        installed_path: code-review.agent.md
        categories: [quality]

  cursor:
    rules:
      - name: review-standards
        description: Code review standards
        file: src/review-checklist.md
        installed_path: review-standards.md
        categories: [quality]
  
  claude:
    commands:
      - name: security-audit
        description: Security audit command
        file: src/security-audit.md
        installed_path: security-audit.md
        categories: [security]`}
          </CodeBlock>
        </div>
      </section>

      <section id="supported-agents" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">
          <a href="#supported-agents" className="hover:text-primary-400 transition-colors">Agent-Specific Artifact Types</a>
        </h2>
        <p className="text-slate-300 mb-4">
          Each AI agent supports specific artifact types that align with their special folder structures. All agents support the universal <code className="bg-slate-700 px-1.5 py-0.5 rounded">files</code> type for generic artifacts.
        </p>
        
        <div className="bg-primary-900/20 border border-primary-700/50 rounded-lg p-4 mb-6">
          <p className="text-slate-300 text-sm">
            <strong className="text-primary-300">💡 Tip:</strong> Use the <code className="bg-slate-700 px-1.5 py-0.5 rounded">files</code> type for any artifact that doesn't fit into agent-specific categories. It works with all agents as a universal catch-all.
          </p>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="py-3 px-4 text-slate-200 font-semibold">Agent</th>
                <th className="py-3 px-4 text-slate-200 font-semibold">Directory</th>
                <th className="py-3 px-4 text-slate-200 font-semibold">Supported Types</th>
                <th className="py-3 px-4 text-slate-200 font-semibold">Notes</th>
              </tr>
            </thead>
            <tbody className="text-slate-300">
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4 font-medium text-primary-400">GitHub Copilot</td>
                <td className="py-3 px-4"><code className="text-sm">.github/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">prompts</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">agents</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">instructions</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">chatmodes</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Prompts, custom agents, repository instructions, and chat modes</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4 font-medium text-primary-400">Claude</td>
                <td className="py-3 px-4"><code className="text-sm">.claude/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">agents</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">commands</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Agent configs and custom commands</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4 font-medium text-primary-400">Cursor</td>
                <td className="py-3 px-4"><code className="text-sm">.cursor/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">rules</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Custom rules for behavior</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4 font-medium text-primary-400">Windsurf</td>
                <td className="py-3 px-4"><code className="text-sm">.windsurf/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">workflows</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">rules</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Workflows and rules</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4 font-medium text-primary-400">Cline</td>
                <td className="py-3 px-4"><code className="text-sm">.cline/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">rules</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">workflows</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Rules and workflows</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4 font-medium text-primary-400">OpenCode</td>
                <td className="py-3 px-4"><code className="text-sm">.opencode/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">commands</code>{' '}
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Commands install to command/ (singular)</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4 font-medium text-primary-400">Gemini</td>
                <td className="py-3 px-4"><code className="text-sm">.gemini/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Files only</td>
              </tr>
              <tr className="border-b border-slate-700/50">
                <td className="py-3 px-4 font-medium text-primary-400">Aider</td>
                <td className="py-3 px-4"><code className="text-sm">.aider/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Files only</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium text-primary-400">Continue</td>
                <td className="py-3 px-4"><code className="text-sm">.continue/</code></td>
                <td className="py-3 px-4">
                  <code className="bg-slate-700 px-1.5 py-0.5 rounded text-xs">files</code>
                </td>
                <td className="py-3 px-4 text-sm text-slate-400">Files only</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section id="publishing" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">
          <a href="#publishing" className="hover:text-primary-400 transition-colors">Publishing Your Package</a>
        </h2>
        <div className="space-y-4 text-slate-300">
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-2xl mr-4">1️⃣</div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Create a Git Repository</h4>
                <p>Host your package on GitHub, GitLab, or any Git hosting service.</p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-2xl mr-4">2️⃣</div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Add Your Manifest</h4>
                <p className="mb-2">Create a <code>dumpty.package.yaml</code> file in the repository root.</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-2xl mr-4">3️⃣</div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Validate Your Manifest</h4>
                <p className="mb-2">Before publishing, validate your manifest to ensure types are correct:</p>
                <div className="bg-slate-900/50 rounded border border-slate-700 p-3 mt-2">
                  <code className="text-primary-300">dumpty validate-manifest dumpty.package.yaml</code>
                </div>
                <p className="mt-2 text-sm text-slate-400">This checks that your manifest can be parsed and all types are supported by each agent.</p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-2xl mr-4">4️⃣</div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Tag Versions</h4>
                <p>Use Git tags for versioning: <code>git tag v1.0.0</code></p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-2xl mr-4">5️⃣</div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Share the URL</h4>
                <p>Users can install with: <code>dumpty install https://github.com/org/your-package</code></p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="best-practices" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">
          <a href="#best-practices" className="hover:text-primary-400 transition-colors">Best Practices</a>
        </h2>
        <div className="bg-primary-900/30 border border-primary-700/50 rounded-lg p-6">
          <ul className="space-y-3 text-slate-300">
            <li>✅ Use semantic versioning (e.g., 1.0.0, 1.1.0, 2.0.0)</li>
            <li>✅ <strong>Validate your manifest</strong> before publishing with <code className="text-primary-300">dumpty validate-manifest</code></li>
            <li>✅ Use appropriate types for each agent (e.g., <code>prompts</code> for Copilot, <code>rules</code> for Cursor)</li>
            <li>✅ Use the universal <code>files</code> type for generic artifacts that don't fit specific categories</li>
            <li>✅ Include a descriptive README.md in your package</li>
            <li>✅ Test your package across different agents</li>
            <li>✅ Keep artifact descriptions clear and concise</li>
            <li>✅ Use meaningful file and artifact names</li>
            <li>✅ Document any dependencies or requirements</li>
          </ul>
        </div>
      </section>
      </div>
      <TableOfContents items={tocItems} />
    </div>
  )
}
