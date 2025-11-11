import CodeBlock from '../components/CodeBlock'
import TableOfContents from '../components/TableOfContents'

const tocItems = [
  { id: 'package-structure', title: 'Package Structure' },
  { id: 'manifest-file', title: 'The Manifest File' },
  { id: 'manifest-fields', title: 'Manifest Fields' },
  { id: 'key-features', title: 'Key Features' },
  { id: 'example-package', title: 'Example Package' },
  { id: 'supported-agents', title: 'Supported Agents & Groups' },
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
          The <code>dumpty.package.yaml</code> file defines your package metadata and what files to install for each AI agent. Files are organized by group (prompts, modes, rules, etc.):
        </p>
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="yaml">
{`name: my-workflows
version: 1.0.0
description: Custom development workflows
manifest_version: 1.0
author: Your Name
repository: https://github.com/org/my-workflows

agents:
  copilot:
    prompts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: code-review.prompt.md
    modes:
      - name: standards
        description: Coding standards mode
        file: src/standards.md
        installed_path: standards.md
  
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
              <li><code className="text-primary-400">repository</code> - Git repository URL (optional)</li>
            </ul>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-semibold mb-2">Agent Configuration</h3>
            <p className="text-slate-300 mb-3">
              Each agent key (<code>copilot</code>, <code>claude</code>, <code>cursor</code>, etc.) contains groups of artifacts:
            </p>
            <ul className="space-y-2 text-slate-300 mb-4">
              <li><strong>Group names</strong> - Organize artifacts by type (e.g., <code>prompts</code>, <code>modes</code>, <code>rules</code>, <code>commands</code>)</li>
              <li><strong>Universal "files" group</strong> - All agents support "files" for generic artifacts</li>
            </ul>
            <p className="text-slate-300 mb-3">Each artifact in a group has:</p>
            <ul className="space-y-2 text-slate-300">
              <li><code className="text-primary-400">name</code> - Artifact identifier</li>
              <li><code className="text-primary-400">description</code> - What this artifact does</li>
              <li><code className="text-primary-400">file</code> - Source file path in your package</li>
              <li><code className="text-primary-400">installed_path</code> - Where to install relative to the group folder</li>
            </ul>
            <p className="text-slate-400 mt-3 text-sm">
              Installation path: <code>{`{agent_dir}/{group}/{package_name}/{installed_path}`}</code>
            </p>
          </div>
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
author: Development Team
repository: https://github.com/org/code-review-workflow

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
    modes:
      - name: review-mode
        description: Code review assistant mode
        file: src/review-mode.md
        installed_path: code-review.md

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
        <h2 className="text-3xl font-semibold mb-4">Supported Agents & Groups</h2>
        <p className="text-slate-300 mb-6">
          Each AI agent supports specific artifact groups that align with their special folder structures. All agents support the universal "files" group for generic artifacts.
        </p>
        <div className="space-y-4">
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">GitHub Copilot</span>
              <code className="text-sm text-slate-400">.github/</code>
            </h3>
            <p className="text-slate-300">Groups: <code>files</code>, <code>prompts</code>, <code>modes</code></p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Claude</span>
              <code className="text-sm text-slate-400">.claude/</code>
            </h3>
            <p className="text-slate-300">Groups: <code>files</code>, <code>agents</code>, <code>commands</code></p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Cursor</span>
              <code className="text-sm text-slate-400">.cursor/</code>
            </h3>
            <p className="text-slate-300">Groups: <code>files</code>, <code>rules</code></p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Windsurf</span>
              <code className="text-sm text-slate-400">.windsurf/</code>
            </h3>
            <p className="text-slate-300">Groups: <code>files</code>, <code>workflows</code>, <code>rules</code></p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Cline</span>
              <code className="text-sm text-slate-400">.cline/</code>
            </h3>
            <p className="text-slate-300">Groups: <code>files</code>, <code>rules</code>, <code>workflows</code></p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <span className="text-primary-400">Gemini / Aider / Continue</span>
              <code className="text-sm text-slate-400">.gemini/ .aider/ .continue/</code>
            </h3>
            <p className="text-slate-300">Groups: <code>files</code> only</p>
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
                <p className="mb-2">Before publishing, validate your manifest to ensure groups are correct:</p>
                <div className="bg-slate-900/50 rounded border border-slate-700 p-3 mt-2">
                  <code className="text-primary-300">dumpty validate-manifest dumpty.package.yaml</code>
                </div>
                <p className="mt-2 text-sm text-slate-400">This checks that your manifest can be parsed and all groups are supported by each agent.</p>
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
            <li>✅ Use appropriate groups for each agent (e.g., <code>prompts</code> for Copilot, <code>rules</code> for Cursor)</li>
            <li>✅ Use the universal <code>files</code> group for generic artifacts that don't fit specific categories</li>
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
