import { motion } from 'framer-motion'
import { AlertCircle, Camera, Leaf } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function NoLeafAlert({ message, confidence }) {
  const { t } = useLanguage()

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6 glass-card p-8 border-2 border-amber-400/50 bg-amber-50/80 dark:bg-amber-950/30"
    >
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-full bg-amber-100 dark:bg-amber-900/50">
          <AlertCircle className="w-8 h-8 text-amber-600" />
        </div>
        <div className="flex-1">
          <h3 className="font-display text-xl font-bold text-amber-900 dark:text-amber-200 mb-2">
            {t('noLeafTitle')}
          </h3>
          <p className="text-amber-800 dark:text-amber-100/90 mb-4">
            {message || t('noLeafMessage')}
          </p>
          {confidence != null && (
            <p className="text-sm text-amber-700 dark:text-amber-300 mb-4">
              {t('noLeafConfidence')}: {confidence}%
            </p>
          )}
          <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li className="flex items-center gap-2">
              <Leaf className="w-4 h-4 text-plant-600 shrink-0" />
              {t('noLeafTip1')}
            </li>
            <li className="flex items-center gap-2">
              <Camera className="w-4 h-4 text-plant-600 shrink-0" />
              {t('noLeafTip2')}
            </li>
          </ul>
        </div>
      </div>
    </motion.div>
  )
}
