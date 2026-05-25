import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Leaf, Brain, Shield, Zap, ArrowRight, Microscope } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function Home() {
  const { t } = useLanguage()

  const features = [
    { icon: Brain, title: 'Deep Learning', desc: 'CNN with MobileNetV2, ResNet50 & EfficientNet transfer learning' },
    { icon: Microscope, title: 'Image Processing', desc: 'OpenCV pipeline: denoise, segment, normalize & edge detection' },
    { icon: Shield, title: 'Expert Guidance', desc: 'Symptoms, causes, prevention & treatment recommendations' },
    { icon: Zap, title: 'Real-time', desc: 'Instant predictions via upload or live webcam scanning' },
  ]

  return (
    <div>
      <section className="relative min-h-[90vh] flex items-center bg-hero-gradient overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-10 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-plant-300 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-7xl mx-auto px-6 py-32 text-center text-white">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Leaf className="w-20 h-20 mx-auto mb-6 text-plant-200" />
            <h1 className="font-display text-5xl md:text-7xl font-bold mb-6">
              Plant Leaf Disease Detection
            </h1>
            <p className="text-xl md:text-2xl text-plant-100 max-w-2xl mx-auto mb-10">
              {t('tagline')}
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link to="/detect" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-plant-800 font-bold rounded-xl hover:bg-plant-50 transition shadow-xl">
                {t('detect')} <ArrowRight className="w-5 h-5" />
              </Link>
              <Link to="/webcam" className="inline-flex items-center gap-2 px-8 py-4 bg-white/20 backdrop-blur border border-white/30 font-semibold rounded-xl hover:bg-white/30 transition">
                {t('webcam')}
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <section id="about" className="py-24 px-6 bg-gray-50 dark:bg-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-display text-4xl font-bold text-gray-900 dark:text-white mb-4">
              AI-Powered Agriculture Platform
            </h2>
            <p className="text-gray-600 dark:text-gray-300 max-w-3xl mx-auto text-lg">
              Our system uses state-of-the-art deep learning and computer vision to identify plant diseases
              from leaf images. Built on the PlantVillage dataset with transfer learning, it delivers
              accurate diagnoses with actionable farming recommendations.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map(({ icon: Icon, title, desc }, i) => (
              <motion.div
                key={title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="glass-card p-6 hover:shadow-2xl transition-shadow"
              >
                <Icon className="w-10 h-10 text-plant-500 mb-4" />
                <h3 className="font-semibold text-lg text-gray-900 dark:text-white mb-2">{title}</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">{desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto glass-card p-12 text-center">
          <h2 className="font-display text-3xl font-bold mb-4 text-gray-900 dark:text-white">
            Supported Diseases
          </h2>
          <div className="flex flex-wrap justify-center gap-3 mt-6">
            {[
              'Tomato Early Blight',
              'Tomato Late Blight',
              'Potato Early Blight',
              'Potato Healthy',
              'Pepper Bacterial Spot',
              'Healthy Leaves',
            ].map((d) => (
              <span
                key={d}
                className="px-4 py-2 bg-plant-100 dark:bg-plant-900/50 text-plant-800 dark:text-plant-200 rounded-full text-sm font-medium"
              >
                {d}
              </span>
            ))}
          </div>
          <Link to="/detect" className="btn-primary inline-flex items-center gap-2 mt-10">
            Start Detection <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  )
}
