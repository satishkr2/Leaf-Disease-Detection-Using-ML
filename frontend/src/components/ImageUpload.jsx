import { useCallback, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, ImageIcon, X, Loader2 } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function ImageUpload({ onPredict, loading, preview }) {
  const { t } = useLanguage()
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState(null)
  const [localPreview, setLocalPreview] = useState(preview)

  const handleFile = useCallback((f) => {
    if (!f?.type.startsWith('image/')) return
    setFile(f)
    setLocalPreview(URL.createObjectURL(f))
  }, [])

  const onDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    handleFile(e.dataTransfer.files[0])
  }

  const onChange = (e) => handleFile(e.target.files[0])

  const clear = () => {
    setFile(null)
    setLocalPreview(null)
  }

  const handlePredict = () => file && onPredict(file)

  return (
    <div className="glass-card p-8">
      <AnimatePresence mode="wait">
        {!localPreview ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            className={`border-2 border-dashed rounded-2xl p-12 text-center transition-colors ${
              dragActive
                ? 'border-plant-500 bg-plant-50 dark:bg-plant-900/30'
                : 'border-plant-300 dark:border-plant-700'
            }`}
          >
            <Upload className="w-16 h-16 mx-auto text-plant-500 mb-4" />
            <p className="text-lg font-medium text-gray-700 dark:text-gray-200">{t('dropHere')}</p>
            <p className="text-sm text-gray-500 mt-2">{t('orBrowse')}</p>
            <input type="file" accept="image/*" onChange={onChange} className="hidden" id="file-upload" />
            <label htmlFor="file-upload" className="btn-primary inline-block mt-6 cursor-pointer">
              {t('upload')}
            </label>
          </motion.div>
        ) : (
          <motion.div key="preview" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            <div className="relative rounded-2xl overflow-hidden bg-gray-100 dark:bg-gray-800">
              <img src={localPreview} alt="Leaf preview" className="w-full max-h-80 object-contain" />
              <button
                onClick={clear}
                className="absolute top-3 right-3 p-2 bg-black/50 rounded-full text-white hover:bg-black/70"
                aria-label="Clear"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <button
              onClick={handlePredict}
              disabled={loading || !file}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {t('analyzingLeaf')}
                </>
              ) : (
                <>
                  <ImageIcon className="w-5 h-5" />
                  {t('detect')}
                </>
              )}
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
