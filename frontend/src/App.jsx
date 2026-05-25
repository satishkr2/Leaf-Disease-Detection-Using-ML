import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Detect from './pages/Detect'
import Webcam from './pages/Webcam'
import Login from './pages/Login'
import Register from './pages/Register'
import History from './pages/History'
import Admin from './pages/Admin'
import Chat from './pages/Chat'

function App() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/detect" element={<Detect />} />
          <Route path="/webcam" element={<Webcam />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/history" element={<History />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
      <footer className="py-8 text-center text-sm text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-800 mt-20">
        Plant Leaf Disease Detection System © {new Date().getFullYear()} · AI + Deep Learning + OpenCV
      </footer>
    </div>
  )
}

export default App
