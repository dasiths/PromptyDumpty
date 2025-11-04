import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import GettingStarted from './pages/GettingStarted'
import CreatingPackages from './pages/CreatingPackages'
import Documentation from './pages/Documentation'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="getting-started" element={<GettingStarted />} />
        <Route path="creating-packages" element={<CreatingPackages />} />
        <Route path="docs" element={<Documentation />} />
      </Route>
    </Routes>
  )
}

export default App
