import { useState } from 'react'
import { motion } from 'framer-motion'
import ImageUpload from '../components/ImageUpload'
import PredictionResult from '../components/PredictionResult'
import { predict } from '../utils/api'
import { formatApiError } from '../utils/api'
import { useLanguage } from '../context/LanguageContext'

export default function Detect() {
  const { t } = useLanguage()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handlePredict = async (file) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await predict(file)
      setResult(res.data)
    } catch (err) {
      setError(formatApiError(err, 'Prediction failed. Is the backend running on port 8000?'))
    } finally {
      setLoading(false)
    }
  }

  const speakResult = (data) => {
    if (!window.speechSynthesis) return
    const text = `${data.disease_name}. Confidence ${data.confidence} percent. ${data.description}`
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9
    window.speechSynthesis.speak(utterance)
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-32">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center mb-10">
        <h1 className="font-display text-4xl font-bold text-gray-900 dark:text-white mb-2">
          {t('upload')}
        </h1>
        <p className="text-gray-600 dark:text-gray-300">{t('tagline')}</p>
      </motion.div>

      <ImageUpload onPredict={handlePredict} loading={loading} />

      {error && (
        <div className="mt-6 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-xl">
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      {result && (
        <div className="mt-10">
          <PredictionResult result={result} onSpeak={speakResult} />
        </div>
      )}
    </div>
  )
}
