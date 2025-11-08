import { useState, useEffect } from 'react'

export default function TableOfContents({ items }) {
  const [activeId, setActiveId] = useState('')

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id)
          }
        })
      },
      { rootMargin: '-80px 0px -80% 0px' }
    )

    // Observe all section headings
    items.forEach((item) => {
      const element = document.getElementById(item.id)
      if (element) observer.observe(element)
    })

    return () => observer.disconnect()
  }, [items])

  const scrollToSection = (id) => {
    const element = document.getElementById(id)
    if (element) {
      const offset = 80
      const elementPosition = element.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.pageYOffset - offset

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      })
    }
  }

  return (
    <nav className="hidden xl:block sticky top-24 w-64 h-fit max-h-[calc(100vh-8rem)] overflow-y-auto">
      <h3 className="text-sm font-semibold text-slate-400 mb-4 uppercase tracking-wider">
        On this page
      </h3>
      <ul className="space-y-2 text-sm">
        {items.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => scrollToSection(item.id)}
              className={`block w-full text-left py-1 px-3 rounded transition-colors ${
                activeId === item.id
                  ? 'text-primary-400 bg-primary-900/20 border-l-2 border-primary-400'
                  : 'text-slate-400 hover:text-slate-300 border-l-2 border-transparent hover:border-slate-600'
              }`}
            >
              {item.title}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  )
}
