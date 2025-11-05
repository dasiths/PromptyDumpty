import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function TerminalBlock({ children, className = '' }) {
  return (
    <div className={`terminal-block rounded-lg overflow-hidden border border-slate-700 ${className}`}>
      {/* Terminal Title Bar */}
      <div className="bg-slate-800 px-4 py-2 flex items-center space-x-2 border-b border-slate-700">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
        </div>
        <div className="text-slate-400 text-sm ml-2">Terminal</div>
      </div>
      
      {/* Terminal Content */}
      <div className="bg-slate-900">
        <SyntaxHighlighter
          language="bash"
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            padding: '1.25rem',
            lineHeight: '1.6',
            background: '#0f172a',
          }}
          showLineNumbers={false}
        >
          {children}
        </SyntaxHighlighter>
      </div>
    </div>
  )
}
