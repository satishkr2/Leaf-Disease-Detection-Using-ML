import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Leaf } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useLanguage } from '../context/LanguageContext'
import { formatApiError } from '../utils/api'

export default function Register() {
  const { register } = useAuth()
  const { t } = useLanguage()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await register(form)
      navigate('/detect')
    } catch (err) {
      setError(formatApiError(err, 'Registration failed'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-32 bg-gradient-to-br from-plant-50 to-plant-100 dark:from-gray-900 dark:to-plant-950">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card w-full max-w-md p-8">
        <div className="text-center mb-8">
          <Leaf className="w-12 h-12 text-plant-500 mx-auto mb-4" />
          <h1 className="font-display text-2xl font-bold">{t('register')}</h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {['email', 'username', 'password'].map((field) => (
            <input
              key={field}
              type={field === 'password' ? 'password' : field === 'email' ? 'email' : 'text'}
              placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
              value={form[field]}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
              required
              className="w-full px-4 py-3 rounded-xl bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:ring-2 focus:ring-plant-500 outline-none"
            />
          ))}
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {t('register')}
          </button>
        </form>
        <p className="text-center mt-6 text-sm">
          <Link to="/login" className="text-plant-600 font-medium">{t('login')}</Link>
        </p>
      </motion.div>
    </div>
  )
}
