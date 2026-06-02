import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Cookie, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const CookieConsent = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookie_consent');
    if (!consent) {
      setIsVisible(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie_consent', 'accepted');
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 md:p-6 pointer-events-none">
      <div className="max-w-4xl mx-auto bg-slate-900 border border-slate-700 shadow-2xl rounded-2xl p-6 pointer-events-auto flex flex-col sm:flex-row gap-6 items-start sm:items-center justify-between">
        <div className="flex gap-4 items-start">
          <div className="bg-indigo-500/20 p-2.5 rounded-full shrink-0">
            <Cookie className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-white font-semibold mb-1">Ми використовуємо cookies</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              Цей веб-сайт використовує файли cookie для забезпечення функціонування системи авторизації, збереження налаштувань локалізації та аналізу трафіку відповідно до GDPR. 
              Детальніше у нашій <Link to="/privacy" className="text-indigo-400 hover:underline">Політиці Конфіденційності</Link>.
            </p>
          </div>
        </div>
        <div className="flex gap-3 w-full sm:w-auto shrink-0 mt-2 sm:mt-0">
          <Button 
            onClick={handleAccept} 
            className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            Прийняти
          </Button>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => setIsVisible(false)} 
            className="text-slate-400 hover:text-white"
            aria-label="Закрити"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  );
};
