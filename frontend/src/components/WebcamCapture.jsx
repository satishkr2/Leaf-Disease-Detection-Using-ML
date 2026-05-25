import { useRef, useState, useEffect } from 'react'
import { Camera, Loader2 } from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

export default function WebcamCapture({ onCapture, loading }) {
  const { t } = useLanguage()
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [stream, setStream] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mediaStream
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: 'environment' } })
      .then((s) => {
        mediaStream = s
        setStream(s)
        if (videoRef.current) videoRef.current.srcObject = s
      })
      .catch(() => setError('Camera access denied. Please allow camera permissions.'))

    return () => mediaStream?.getTracks().forEach((track) => track.stop())
  }, [])

  const capture = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' })
        onCapture(file)
      }
    }, 'image/jpeg', 0.9)
  }

  return (
    <div className="glass-card p-6 space-y-4">
      {error ? (
        <p className="text-red-500 text-center py-8">{error}</p>
      ) : (
        <>
          <div className="relative rounded-2xl overflow-hidden bg-black aspect-video">
            <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
          </div>
          <canvas ref={canvasRef} className="hidden" />
          <button
            onClick={capture}
            disabled={loading || !stream}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Camera className="w-5 h-5" />
            )}
            {loading ? t('analyzing') : t('detect')}
          </button>
        </>
      )}
    </div>
  )
}
