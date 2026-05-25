import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Send, Bot, User } from 'lucide-react'
import { chat } from '../utils/api'
import { useLanguage } from '../context/LanguageContext'

export default function Chatbot() {
  const { lang, t } = useLanguage()
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hello! I'm your PlantCare farming assistant. Ask about watering, pests, fertilizer, or crop care!" },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages((m) => [...m, { role: 'user', text: userMsg }])
    setLoading(true)
    try {
      const res = await chat(userMsg, lang)
      setMessages((m) => [...m, { role: 'bot', text: res.data.reply }])
    } catch {
      setMessages((m) => [...m, { role: 'bot', text: 'Sorry, I could not connect. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="glass-card flex flex-col h-[500px]">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2">
        <Bot className="w-6 h-6 text-plant-500" />
        <h3 className="font-semibold">{t('chatbot')}</h3>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`p-2 rounded-full ${msg.role === 'bot' ? 'bg-plant-100 dark:bg-plant-900/50' : 'bg-gray-200 dark:bg-gray-700'}`}>
              {msg.role === 'bot' ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
            </div>
            <div
              className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm ${
                msg.role === 'user'
                  ? 'bg-plant-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200'
              }`}
            >
              {msg.text}
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex gap-1 px-4">
            <span className="w-2 h-2 bg-plant-500 rounded-full animate-bounce" />
            <span className="w-2 h-2 bg-plant-500 rounded-full animate-bounce delay-100" />
            <span className="w-2 h-2 bg-plant-500 rounded-full animate-bounce delay-200" />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Ask about farming..."
          className="flex-1 px-4 py-2 rounded-xl bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-plant-500"
        />
        <button onClick={send} disabled={loading} className="btn-primary p-3">
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}
