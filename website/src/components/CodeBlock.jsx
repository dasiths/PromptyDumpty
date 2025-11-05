import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function CodeBlock({ children, language = 'bash', className = '' }) {
  return (
    <div className={`code-block rounded-lg overflow-hidden ${className}`}>
      <SyntaxHighlighter
        language={language}
        style={vscDarkPlus}
        customStyle={{
          margin: 0,
          padding: '1.25rem',
          lineHeight: '1.6',
          background: '#1e293b',
        }}
        showLineNumbers={false}
      >
        {children}
      </SyntaxHighlighter>
    </div>
  )
}
