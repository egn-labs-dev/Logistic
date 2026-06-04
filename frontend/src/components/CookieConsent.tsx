import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Cookie, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';

export const CookieConsent = () => {
  const [isVisible, setIsVisible] = useState(() => !localStorage.getItem('cookie_consent'));
  const { t } = useTranslation();

  const handleAccept = () => {
    localStorage.setItem('cookie_consent', 'accepted');
    setIsVisible(false);
  };

  const handleDecline = () => {
    localStorage.setItem('cookie_consent', 'declined');
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
            <h3 className="text-white font-semibold mb-1">{t('cookie.title', 'Ми використовуємо файли cookie')}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">
              {t('cookie.description', 'Цей сайт використовує необхідні файли cookie для безпечного керування сесіями. Ми не використовуємо рекламні трекери.')} <Link to="/privacy" className="text-indigo-400 hover:underline">{t('cookie.privacy_link')}</Link>.
            </p>
          </div>
        </div>
        <div className="flex gap-3 w-full sm:w-auto shrink-0 mt-2 sm:mt-0">
          <Button variant="outline" size="sm" onClick={handleDecline}>
            {t('cookie.close', 'Закрити')}
          </Button>
          <Button 
            onClick={handleAccept} 
            className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            <Check className="w-5 h-5 mr-1" /> {t('cookie.accept', 'Accept')}
          </Button>
        </div>
      </div>
    </div>
  );
};
