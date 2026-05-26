import { useState } from 'react'
import { motion } from 'framer-motion'
import WebcamCapture from '../components/WebcamCapture'
import PredictionResult from '../components/PredictionResult'
import NoLeafAlert from '../components/NoLeafAlert'
import { predict, parseApiError } from '../utils/api'
import { useLanguage } from '../context/LanguageContext'

export default function Webcam() {
  const { t } = useLanguage()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [noLeaf, setNoLeaf] = useState(null)

  const handleCapture = async (file) => {
    setLoading(true)
    setError(null)
    setNoLeaf(null)
    setResult(null)
    try {
      const res = await predict(file)
      setResult(res.data)
    } catch (err) {
      const parsed = parseApiError(err, 'Prediction failed')
      if (parsed.code === 'NO_LEAF_DETECTED') {
        setNoLeaf(parsed)
      } else {
        setError(parsed.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const speakResult = (data) => {
    const utterance = new SpeechSynthesisUtterance(
      `${data.disease_name}. ${data.confidence} percent confidence. ${data.description}`
    )
    window.speechSynthesis?.speak(utterance)
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-32">
      <motion.h1
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-display text-4xl font-bold text-center mb-10 text-gray-900 dark:text-white"
      >
        {t('webcam')}
      </motion.h1>
      <WebcamCapture onCapture={handleCapture} loading={loading} />
      {noLeaf && <NoLeafAlert message={noLeaf.message} confidence={noLeaf.confidence} />}
      {error && <p className="mt-4 text-red-500 text-center">{error}</p>}
      {result && (
        <div className="mt-10">
          <PredictionResult result={result} onSpeak={speakResult} />
        </div>
      )}
    </div>
  )
}
