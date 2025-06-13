import { useState } from 'react'
import {Routes, Route} from 'react-router-dom'
import Navbar from './components/NavBar.jsx'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import Set from './pages/Set.jsx'
import Flashcard from './pages/Flashcard.jsx'
function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/set" element={<Set />} />
        <Route path="/flashcard" element={<Flashcard />} />
      </Routes>
    </div>
  )
}

export default App
