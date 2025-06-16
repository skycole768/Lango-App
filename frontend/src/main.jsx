import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import NavBar from './components/NavBar.jsx'  

import '../src/styles/Global.css'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <NavBar/>
      <App/>
    </BrowserRouter>
  </StrictMode>
)
