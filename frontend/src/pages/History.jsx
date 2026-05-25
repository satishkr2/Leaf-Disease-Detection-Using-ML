import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { History as HistoryIcon, Download, ChevronRight } from 'lucide-react'
import { getHistory, downloadReport } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { useLanguage } from '../context/LanguageContext'

export default function History() {
  const { user } = useAuth()
  const { t } = useLanguage()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    getHistory()
      .then((res) => setItems(res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [user])

  const handleDownload = async (id) => {
    const res = await downloadReport(id)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${id}.pdf`
    a.click()
  }

  if (!user) {
    return (
      <div className="text-center py-32">
        <p className="mb-4">Please login to view history</p>
        <Link to="/login" className="btn-primary">{t('login')}</Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-32">
      <h1 className="font-display text-4xl font-bold mb-8 flex items-center gap-3">
        <HistoryIcon className="w-10 h-10 text-plant-500" />
        {t('history')}
      </h1>

      {loading ? (
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-gray-200 dark:bg-gray-700 rounded-xl" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="glass-card p-12 text-center text-gray-500">
          No predictions yet. <Link to="/detect" className="text-plant-600">Start detecting</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-card p-6 flex items-center justify-between"
            >
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">{item.disease_name}</h3>
                <p className="text-sm text-gray-500">
                  {item.confidence}% · {new Date(item.created_at).toLocaleString()}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownload(item.id)}
                  className="p-2 rounded-lg hover:bg-plant-100 dark:hover:bg-plant-900/50"
                  title={t('downloadReport')}
                >
                  <Download className="w-5 h-5 text-plant-600" />
                </button>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
