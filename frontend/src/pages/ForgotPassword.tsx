import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle2, Loader2, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/button';
import apiClient from '@/api/client';
import { useTranslation } from 'react-i18next';

export const ForgotPassword = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    
    try {
      await apiClient.post('/auth/forgot-password', { email });
      setSuccess(true);
    } catch {
      setErrorMsg(t('auth.error_generic', 'Помилка при відправці запиту. Спробуйте пізніше.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
        <div className="text-center mb-8">
          <div className="mx-auto w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-4">
            <Mail className="w-6 h-6 text-indigo-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">{t('auth.forgot_password_title')}</h1>
          <p className="text-slate-500 text-sm">{t('auth.forgot_password_desc')}</p>
        </div>

        {success ? (
          <div className="text-center">
            <div className="bg-green-50 text-green-700 p-4 rounded-xl mb-6 flex flex-col items-center">
              <CheckCircle2 className="w-10 h-10 mb-2" />
              <p className="font-medium">{t('auth.email_sent')}</p>
              <p className="text-sm mt-1">{t('auth.check_inbox')} <strong>{email}</strong>.</p>
            </div>
            <Button asChild variant="outline" className="w-full">
              <Link to="/login"><ArrowLeft className="w-4 h-4 mr-2" /> {t('auth.back_to_login')}</Link>
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
                {t('auth.email')}
              </label>
              <input 
                type="email" 
                id="email" 
                className="w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required 
              />
            </div>

            {errorMsg && (
              <div className="p-3 bg-red-50 rounded-md border border-red-100 flex items-start space-x-2 text-sm text-red-700">
                <ShieldAlert className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <Button type="submit" className="w-full h-11 bg-indigo-600 hover:bg-indigo-700" disabled={loading}>
              {loading ? <Loader2 className="animate-spin w-5 h-5" /> : t('auth.send_link')}
            </Button>
            
            <div className="text-center pt-4">
              <Link to="/login" className="text-sm text-slate-500 hover:text-indigo-600 font-medium inline-flex items-center">
                <ArrowLeft className="w-4 h-4 mr-1" /> {t('auth.back_to_login')}
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
