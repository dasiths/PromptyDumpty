import CodeBlock from '../components/CodeBlock'
import TableOfContents from '../components/TableOfContents'

const tocItems = [
  { id: 'package-structure', title: 'Package Structure' },
  { id: 'manifest-file', title: 'The Manifest File' },
  { id: 'manifest-fields', title: 'Manifest Fields' },
  { id: 'key-features', title: 'Key Features' },
  { id: 'external-repos', title: 'External Repository References' },
  { id: 'example-package', title: 'Example Package' },
  { id: 'supported-agents', title: 'Agent-Specific Artifact Types' },
  { id: 'publishing', title: 'Publishing Your Package' },
  { id: 'best-practices', title: 'Best Practices' },
]

export default function CreatingPackages() {
  return (
    <div className="flex gap-8 max-w-7xl mx-auto px-4 py-12">
      <div className="flex-1 min-w-0 text-white">
        <h1 className="text-4xl font-bold mb-8">Creating Packages</h1>

        <section id="package-structure" className="mb-12 scroll-mt-24">
          <h2 className="text-3xl font-semibold mb-4">Package Structure</h2>
        <p className="text-slate-300 mb-4">
          A PromptyDumpty package is simply a Git repository with a <code>dumpty.package.yaml</code> manifest file. You can organize your files however you want!
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
        <h2 className="text-3xl font-semibold mb-4">The Manifest File</h2>
        <p className="text-slate-300 mb-4">
          The <code>dumpty.package.yaml</code> file defines your package metadata and what files to install for each AI agent. Files are organized by type (prompts, agents, rules, etc.):
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
        <h2 className="text-3xl font-semibold mb-4">Manifest Fields</h2>
        
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

      <section id="key-features" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Key Features</h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="text-3xl mb-3">🗂️</div>
            <h3 className="text-xl font-semibold mb-2">Flexible Organization</h3>
            <p className="text-slate-300">
              Organize your source files however makes sense. The manifest maps them to installation paths.
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="text-3xl mb-3">♻️</div>
            <h3 className="text-xl font-semibold mb-2">File Reuse</h3>
            <p className="text-slate-300">
              Use the same source file for multiple agents by mapping it to different installed paths.
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="text-3xl mb-3">🎯</div>
            <h3 className="text-xl font-semibold mb-2">Precise Control</h3>
            <p className="text-slate-300">
              Explicitly define where each file should be installed for each agent.
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="text-3xl mb-3">📦</div>
            <h3 className="text-xl font-semibold mb-2">Multi-Agent Support</h3>
            <p className="text-slate-300">
              Create one package that works across all supported AI coding assistants.
            </p>
          </div>
        </div>
      </section>

      <section id="external-repos" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">External Repository References</h2>
        
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
        <h2 className="text-3xl font-semibold mb-4">Example Package</h2>
        <p className="text-slate-300 mb-4">
          Here's a complete example of a code review workflow package:
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
    └── performance-tips.md`}
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

agents:
  copilot:
    prompts:
      - name: review-checklist
        description: Code review checklist
        file: src/review-checklist.md
        installed_path: review.prompt.md
      
      - name: security-audit
        description: Security review guidelines
        file: src/security-audit.md
        installed_path: security.prompt.md
    agents:
      - name: review-mode
        description: Code review assistant agent
        file: src/review-mode.md
        installed_path: code-review.agent.md

  cursor:
    rules:
      - name: review-standards
        file: src/review-checklist.md
        installed_path: review-standards.md
  
  claude:
    commands:
      - name: security-audit
        file: src/security-audit.md
        installed_path: security-audit.md`}
          </CodeBlock>
        </div>
      </section>

      <section id="supported-agents" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Agent-Specific Artifact Types</h2>
        <p className="text-slate-300 mb-4">
          Each AI agent supports specific artifact types that align with their special folder structures. All agents support the universal <code className="bg-slate-700 px-1.5 py-0.5 rounded">files</code> type for generic artifacts.
        </p>
        
        <div className="bg-primary-900/20 border border-primary-700/50 rounded-lg p-4 mb-6">
          <p className="text-slate-300 text-sm">
            <strong className="text-primary-300">💡 Tip:</strong> Use the <code className="bg-slate-700 px-1.5 py-0.5 rounded">files</code> type for any artifact that doesn't fit into agent-specific categories. It works with all agents as a universal catch-all.
          </p>
        </div>

        <div className="space-y-4">
          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">GitHub Copilot</span>
              <code className="text-sm text-slate-400 font-normal">.github/</code>
            </h3>
            <p className="text-slate-300 mb-2">
              <strong>Types:</strong> <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">files</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">prompts</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">agents</code>
            </p>
            <p className="text-slate-400 text-sm">
              Supports custom prompts and agents for the Copilot chat interface
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Claude</span>
              <code className="text-sm text-slate-400 font-normal">.claude/</code>
            </h3>
            <p className="text-slate-300 mb-2">
              <strong>Types:</strong> <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">files</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">agents</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">commands</code>
            </p>
            <p className="text-slate-400 text-sm">
              Supports agent configurations and custom commands
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Cursor</span>
              <code className="text-sm text-slate-400 font-normal">.cursor/</code>
            </h3>
            <p className="text-slate-300 mb-2">
              <strong>Types:</strong> <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">files</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">rules</code>
            </p>
            <p className="text-slate-400 text-sm">
              Supports custom rules that guide Cursor's behavior
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Windsurf</span>
              <code className="text-sm text-slate-400 font-normal">.windsurf/</code>
            </h3>
            <p className="text-slate-300 mb-2">
              <strong>Types:</strong> <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">files</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">workflows</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">rules</code>
            </p>
            <p className="text-slate-400 text-sm">
              Supports custom workflows and rules
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Cline</span>
              <code className="text-sm text-slate-400 font-normal">.cline/</code>
            </h3>
            <p className="text-slate-300 mb-2">
              <strong>Types:</strong> <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">files</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">rules</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">workflows</code>
            </p>
            <p className="text-slate-400 text-sm">
              Supports rules and workflows for customization
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Gemini / Aider / Continue</span>
              <code className="text-sm text-slate-400 font-normal">.gemini/ .aider/ .continue/</code>
            </h3>
            <p className="text-slate-300 mb-2">
              <strong>Types:</strong> <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">files</code> only
            </p>
            <p className="text-slate-400 text-sm">
              These agents only support the universal files type for generic artifacts
            </p>
          </div>
        </div>
      </section>

      <section id="publishing" className="mb-12 scroll-mt-24">
        <h2 className="text-3xl font-semibold mb-4">Publishing Your Package</h2>
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
        <h2 className="text-3xl font-semibold mb-4">Best Practices</h2>
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
