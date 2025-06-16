import { useState } from 'react'
import {Routes, Route} from 'react-router-dom'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import Set from './pages/Set.jsx'
import Flashcard from './pages/Flashcard.jsx'
import EditFlashcard from './pages/EditFlashcard.jsx'
import AddSet from './pages/AddSet.jsx'
import AddFlashcard from './pages/AddFlashcard.jsx'
import AddLanguage from './pages/AddLanguage.jsx'
import EditSet from './pages/EditSet.jsx'
import Profile from './pages/Profile.jsx'
function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/set/:language_id" element={<Set />} />
        <Route path="/flashcard/:language_id/:set_id" element={<Flashcard />} />
        <Route path="/edit-flashcard/:language_id/:set_id/:flashcard_id" element={<EditFlashcard />} />
        <Route path="/add-set/:language_id" element={<AddSet />} />
        <Route path="/add-flashcard/:language_id/:set_id" element={<AddFlashcard />} />
        <Route path="/edit-set/:language_id/:set_id" element={<EditSet />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/add-language" element={<AddLanguage />} />
      </Routes>
    </div>
  )
}

export default App
