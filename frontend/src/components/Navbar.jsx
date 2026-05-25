import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Leaf, Moon, Sun, Globe, LogOut, User, Shield } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import { useLanguage } from '../context/LanguageContext'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { dark, toggle } = useTheme()
  const { lang, setLanguage, t } = useLanguage()
  const { user, logout } = useAuth()
  const location = useLocation()

  const links = [
    { to: '/', label: t('about') === 'About' ? 'Home' : 'Inicio', path: '/' },
    { to: '/detect', label: t('detect') },
    { to: '/webcam', label: t('webcam') },
    { to: '/chat', label: t('chatbot') },
  ]

  if (user) links.push({ to: '/history', label: t('history') })
  if (user?.is_admin) links.push({ to: '/admin', label: t('admin'), icon: Shield })

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed top-0 left-0 right-0 z-50 glass-card mx-4 mt-4 px-6 py-3"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-display font-bold text-xl text-plant-700 dark:text-plant-400">
          <Leaf className="w-8 h-8 text-plant-500" />
          {t('appName')}
        </Link>

        <div className="hidden md:flex items-center gap-6">
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={`text-sm font-medium transition-colors ${
                location.pathname === l.to
                  ? 'text-plant-600 dark:text-plant-400'
                  : 'text-gray-600 dark:text-gray-300 hover:text-plant-600'
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <select
            value={lang}
            onChange={(e) => setLanguage(e.target.value)}
            className="text-sm bg-transparent border border-plant-200 dark:border-plant-700 rounded-lg px-2 py-1"
            aria-label="Language"
          >
            <option value="en">EN</option>
            <option value="es">ES</option>
            <option value="hi">HI</option>
          </select>
          <button onClick={toggle} className="p-2 rounded-lg hover:bg-plant-100 dark:hover:bg-plant-900/50" aria-label="Toggle theme">
            {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          {user ? (
            <div className="flex items-center gap-2">
              <span className="hidden sm:flex items-center gap-1 text-sm text-gray-600 dark:text-gray-300">
                <User className="w-4 h-4" /> {user.username}
              </span>
              <button onClick={logout} className="p-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600" aria-label="Logout">
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn-primary text-sm py-2 px-4">{t('login')}</Link>
          )}
        </div>
      </div>
    </motion.nav>
  )
}
