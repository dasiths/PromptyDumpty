import CodeBlock from '../components/CodeBlock'

export default function CreatingPackages() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 text-white">
      <h1 className="text-4xl font-bold mb-8">Creating Packages</h1>

      <section className="mb-12">
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

      <section className="mb-12">
        <h2 className="text-3xl font-semibold mb-4">The Manifest File</h2>
        <p className="text-slate-300 mb-4">
          The <code>dumpty.package.yaml</code> file defines your package metadata and what files to install for each AI agent:
        </p>
        <div className="border border-slate-700 mb-6">
          <CodeBlock language="yaml">
{`name: my-workflows
version: 1.0.0
description: Custom development workflows
author: Your Name
repository: https://github.com/org/my-workflows

agents:
  copilot:
    artifacts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: prompts/code-review.prompt.md
      
      - name: standards
        description: Coding standards
        file: src/standards.md
        installed_path: rules/standards.md
  
  claude:
    artifacts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: commands/review.md`}
          </CodeBlock>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-3xl font-semibold mb-4">Manifest Fields</h2>
        
        <div className="space-y-6">
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-semibold mb-2">Package Metadata</h3>
            <ul className="space-y-2 text-slate-300">
              <li><code className="text-primary-400">name</code> - Package name (required)</li>
              <li><code className="text-primary-400">version</code> - Semantic version (required)</li>
              <li><code className="text-primary-400">description</code> - Brief description (required)</li>
              <li><code className="text-primary-400">author</code> - Package author (optional)</li>
              <li><code className="text-primary-400">repository</code> - Git repository URL (optional)</li>
            </ul>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-semibold mb-2">Agent Configuration</h3>
            <p className="text-slate-300 mb-3">
              Each agent key (<code>copilot</code>, <code>claude</code>, <code>cursor</code>, etc.) contains an <code>artifacts</code> list:
            </p>
            <ul className="space-y-2 text-slate-300">
              <li><code className="text-primary-400">name</code> - Artifact identifier</li>
              <li><code className="text-primary-400">description</code> - What this artifact does</li>
              <li><code className="text-primary-400">file</code> - Source file path in your package</li>
              <li><code className="text-primary-400">installed_path</code> - Where to install relative to agent's root</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="mb-12">
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
              Create one package that works across all supported AI agents.
            </p>
          </div>
        </div>
      </section>

      <section className="mb-12">
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
└── prompts/
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
author: Development Team
repository: https://github.com/org/code-review-workflow

agents:
  copilot:
    artifacts:
      - name: review-checklist
        description: Code review checklist
        file: prompts/review-checklist.md
        installed_path: prompts/review.prompt.md
      
      - name: security-audit
        description: Security review guidelines
        file: prompts/security-audit.md
        installed_path: prompts/security.prompt.md
      
      - name: performance
        description: Performance optimization tips
        file: prompts/performance-tips.md
        installed_path: rules/performance.md

  claude:
    artifacts:
      - name: review-checklist
        file: prompts/review-checklist.md
        installed_path: commands/code-review.md
      
      - name: security-audit
        file: prompts/security-audit.md
        installed_path: commands/security-audit.md`}
          </CodeBlock>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-3xl font-semibold mb-4">Supported Agents</h2>
        <p className="text-slate-300 mb-4">
          You can create packages for the following agents:
        </p>
        <div className="grid md:grid-cols-2 gap-4 text-slate-300">
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <code className="text-primary-400">copilot</code> - GitHub Copilot
          </div>
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <code className="text-primary-400">claude</code> - Claude
          </div>
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <code className="text-primary-400">cursor</code> - Cursor
          </div>
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <code className="text-primary-400">gemini</code> - Gemini
          </div>
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <code className="text-primary-400">windsurf</code> - Windsurf
          </div>
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <code className="text-primary-400">cline</code> - Cline
          </div>
        </div>
      </section>

      <section className="mb-12">
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
                <p>Create a <code>dumpty.package.yaml</code> file in the repository root.</p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-2xl mr-4">3️⃣</div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Tag Versions</h4>
                <p>Use Git tags for versioning: <code>git tag v1.0.0</code></p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <div className="flex items-start">
              <div className="text-2xl mr-4">4️⃣</div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">Share the URL</h4>
                <p>Users can install with: <code>dumpty install https://github.com/org/your-package</code></p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-3xl font-semibold mb-4">Best Practices</h2>
        <div className="bg-primary-900/30 border border-primary-700/50 rounded-lg p-6">
          <ul className="space-y-3 text-slate-300">
            <li>✅ Use semantic versioning (e.g., 1.0.0, 1.1.0, 2.0.0)</li>
            <li>✅ Include a descriptive README.md in your package</li>
            <li>✅ Test your package across different agents</li>
            <li>✅ Keep artifact descriptions clear and concise</li>
            <li>✅ Use meaningful file and artifact names</li>
            <li>✅ Document any dependencies or requirements</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
