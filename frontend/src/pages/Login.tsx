import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Loader2, Lock, ShieldCheck, LogIn } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { useTranslation } from 'react-i18next';
import apiClient from '@/api/client';
import { useAuthStore } from '@/store/authStore';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const setToken = useAuthStore((state) => state.setToken);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      // OAuth2 requires application/x-www-form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token } = response.data;
      setToken(access_token);
      navigate('/');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      if (error.response?.status === 401 || error.response?.status === 400) {
        setErrorMsg(t('auth.error_login'));
      } else {
        setErrorMsg(t('auth.error_server'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 p-4 relative">
      <div className="absolute top-4 right-4 bg-white/80 backdrop-blur rounded-lg shadow-sm">
        <LanguageSwitcher className="text-slate-700 hover:text-slate-900" />
      </div>
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-indigo-600 p-3 rounded-xl mb-4">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Zero Trust Dispatch</h1>
          <p className="text-slate-500 mt-2 text-center">{t('auth.login_title')}</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">{t('auth.email')}</label>
            <Input 
              type="email" 
              placeholder="dispatcher@cargo.com" 
              className="h-11" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center mb-1">
              <label htmlFor="password" className="block text-sm font-medium text-slate-700">
                {t('auth.password')}
              </label>
              <Link to="/forgot-password" className="text-xs font-medium text-indigo-600 hover:text-indigo-500">
                {t('auth.forgot_password', 'Забули пароль?')}
              </Link>
            </div>
            <Input 
              type="password" 
              placeholder="••••••••" 
              className="h-11" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          {errorMsg && (
            <div className="p-3 bg-red-50 rounded-md border border-red-100 flex items-start space-x-2">
              <Lock className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
              <p className="text-sm text-red-600 leading-tight">{errorMsg}</p>
            </div>
          )}

          <Button type="submit" className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 mt-4 transition-colors" disabled={loading}>
            {loading ? (
              <><Loader2 className="animate-spin w-5 h-5 mr-2" /> {t('auth.logging_in')}</>
            ) : (
              <><LogIn className="w-5 h-5 mr-2" /> {t('auth.login_btn')}</>
            )}
          </Button>

          <div className="text-center pt-4 mt-2 border-t border-slate-100 text-sm text-slate-600">
            {t('auth.no_account')} <Link to="/register" className="text-indigo-600 hover:text-indigo-700 font-medium ml-1">{t('auth.register')}</Link>
          </div>
        </form>

        <div className="mt-8 flex justify-center items-center gap-2 text-slate-400 text-sm">
          <Lock className="w-4 h-4" />
          <span>{t('auth.encryption_notice', "З'єднання зашифровано (AES-256)")}</span>
        </div>
      </div>
    </div>
  );
};
