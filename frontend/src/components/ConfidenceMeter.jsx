import { motion } from 'framer-motion'

export default function ConfidenceMeter({ value }) {
  const pct = Math.min(100, Math.max(0, value))
  const color = pct >= 80 ? 'bg-plant-500' : pct >= 60 ? 'bg-yellow-500' : 'bg-orange-500'

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm mb-2">
        <span className="text-gray-600 dark:text-gray-400">Confidence</span>
        <span className="font-bold text-plant-700 dark:text-plant-400">{pct.toFixed(1)}%</span>
      </div>
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className={`h-full ${color} rounded-full`}
        />
      </div>
    </div>
  )
}
