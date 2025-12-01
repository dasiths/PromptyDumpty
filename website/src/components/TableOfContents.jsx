import { useState, useEffect } from 'react'

export default function TableOfContents({ items }) {
  const [activeId, setActiveId] = useState('')

  useEffect(() => {
    const handleScroll = () => {
      // Get all section elements
      const sections = items.map(item => ({
        id: item.id,
        element: document.getElementById(item.id)
      })).filter(s => s.element)

      // Find which section is currently in view
      // We consider a section "active" if its top is above the middle of the screen
      const scrollPosition = window.scrollY + 150 // 150px offset from top

      // Go through sections in reverse order to find the last one that's above scroll position
      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sections[i]
        const sectionTop = section.element.offsetTop

        if (scrollPosition >= sectionTop) {
          setActiveId(section.id)
          return
        }
      }

      // If we're at the very top, activate the first section
      if (sections.length > 0) {
        setActiveId(sections[0].id)
      }
    }

    // Scroll to anchor on page load
    const hash = window.location.hash
    if (hash) {
      const id = hash.replace('#', '')
      const element = document.getElementById(id)
      if (element) {
        // Use setTimeout to ensure page is fully rendered
        setTimeout(() => {
          const offset = 80
          const elementPosition = element.getBoundingClientRect().top
          const offsetPosition = elementPosition + window.pageYOffset - offset

          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          })
          setActiveId(id)
        }, 100)
      }
    }

    // Initial check
    handleScroll()

    // Add scroll listener
    window.addEventListener('scroll', handleScroll, { passive: true })
    
    return () => window.removeEventListener('scroll', handleScroll)
  }, [items])

  const scrollToSection = (id) => {
    const element = document.getElementById(id)
    if (element) {
      // Update URL with anchor
      window.history.pushState(null, '', `#${id}`)
      
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
