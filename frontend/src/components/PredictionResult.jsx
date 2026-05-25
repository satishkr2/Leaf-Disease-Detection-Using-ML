import { motion } from 'framer-motion'
import {
  AlertTriangle,
  CheckCircle,
  Pill,
  Shield,
  Stethoscope,
  Leaf,
  Download,
  Volume2,
} from 'lucide-react'
import ConfidenceMeter from './ConfidenceMeter'
import { useLanguage } from '../context/LanguageContext'
import { downloadReport, processedImageUrl } from '../utils/api'

export default function PredictionResult({ result, onSpeak }) {
  const { t } = useLanguage()
  if (!result) return null

  const isHealthy = result.disease_name?.toLowerCase().includes('healthy')
  const apiBase = import.meta.env.VITE_API_URL || ''

  const handleDownload = async () => {
    if (!result.id) return
    try {
      const res = await downloadReport(result.id)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `plant_report_${result.id}.pdf`
      a.click()
    } catch (e) {
      console.error(e)
    }
  }

  const processedSrc = result.processed_image_url
    ? `${apiBase}${result.processed_image_url}`
    : null

  const sections = [
    { icon: Stethoscope, title: t('symptoms'), content: result.symptoms, color: 'text-orange-500' },
    { icon: AlertTriangle, title: t('causes'), content: result.causes, color: 'text-red-500' },
    { icon: Shield, title: t('prevention'), content: result.prevention, color: 'text-blue-500' },
    { icon: Pill, title: t('treatment'), content: result.prescription, color: 'text-purple-500' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="glass-card p-8">
        <div className="flex items-start gap-4 mb-6">
          {isHealthy ? (
            <CheckCircle className="w-12 h-12 text-plant-500 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-12 h-12 text-amber-500 flex-shrink-0" />
          )}
          <div className="flex-1">
            <h2 className="font-display text-2xl font-bold text-gray-900 dark:text-white">
              {result.disease_name}
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mt-2">{result.description}</p>
          </div>
        </div>
        <ConfidenceMeter value={result.confidence} />
        <div className="flex flex-wrap gap-3 mt-6">
          {result.id && (
            <button onClick={handleDownload} className="btn-secondary flex items-center gap-2 text-sm">
              <Download className="w-4 h-4" /> {t('downloadReport')}
            </button>
          )}
          {onSpeak && (
            <button onClick={() => onSpeak(result)} className="btn-secondary flex items-center gap-2 text-sm">
              <Volume2 className="w-4 h-4" /> {t('voiceExplain')}
            </button>
          )}
        </div>
      </div>

      {processedSrc && (
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Leaf className="w-5 h-5 text-plant-500" /> Preprocessing Pipeline
          </h3>
          <img src={processedSrc} alt="Processed leaf" className="rounded-xl max-h-48 mx-auto" />
          {result.preprocessing_steps?.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4 justify-center">
              {result.preprocessing_steps.map((step, i) => (
                <span
                  key={i}
                  className="px-3 py-1 text-xs bg-plant-100 dark:bg-plant-900/50 text-plant-700 dark:text-plant-300 rounded-full"
                >
                  {step}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {sections.map(({ icon: Icon, title, content, color }, i) => (
          <motion.div
            key={title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-6"
          >
            <h3 className={`font-semibold flex items-center gap-2 mb-3 ${color}`}>
              <Icon className="w-5 h-5" /> {title}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{content}</p>
          </motion.div>
        ))}
      </div>

      {result.top_predictions?.length > 1 && (
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">Top Predictions</h3>
          <div className="space-y-2">
            {result.top_predictions.map((p, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-300 truncate max-w-[70%]">
                  {p.label?.replace(/___/g, ' ')}
                </span>
                <span className="font-medium text-plant-600">{p.confidence}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
