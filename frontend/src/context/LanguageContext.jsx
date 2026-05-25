import { createContext, useContext, useState } from 'react'
import { t } from '../utils/i18n'

const LanguageContext = createContext()

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem('lang') || 'en')

  const setLanguage = (l) => {
    setLang(l)
    localStorage.setItem('lang', l)
  }

  const translate = (key) => t(lang, key)

  return (
    <LanguageContext.Provider value={{ lang, setLanguage, t: translate }}>
      {children}
    </LanguageContext.Provider>
  )
}

export const useLanguage = () => useContext(LanguageContext)
