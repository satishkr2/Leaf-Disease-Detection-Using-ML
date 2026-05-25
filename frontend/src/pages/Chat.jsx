import { motion } from 'framer-motion'
import Chatbot from '../components/Chatbot'
import { useLanguage } from '../context/LanguageContext'

export default function Chat() {
  const { t } = useLanguage()

  return (
    <div className="max-w-2xl mx-auto px-6 py-32">
      <motion.h1
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-display text-4xl font-bold text-center mb-8 text-gray-900 dark:text-white"
      >
        {t('chatbot')}
      </motion.h1>
      <Chatbot />
    </div>
  )
}
