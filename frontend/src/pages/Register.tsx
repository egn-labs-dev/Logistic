import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Loader2, Lock, ShieldCheck, UserPlus, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { useTranslation } from 'react-i18next';
import apiClient from '@/api/client';
import { useAuthStore } from '@/store/authStore';
import { AxiosError } from 'axios';

export const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [orgId, setOrgId] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const setToken = useAuthStore((state) => state.setToken);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      // 1. Реєстрація
      await apiClient.post('/auth/register', {
        email,
        password,
        organization_id: orgId
      });

      // 2. Автоматичний логін після успішної реєстрації
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const loginRes = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token } = loginRes.data;
      setToken(access_token);
      navigate('/');
    } catch (error: unknown) {
      if (error instanceof AxiosError && error.response?.status === 400) {
        setErrorMsg(t('auth.email_exists'));
      } else {
        setErrorMsg(t('auth.register_error'));
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
        <div className="flex flex-col items-center mb-6">
          <div className="bg-indigo-600 p-3 rounded-xl mb-4 shadow-lg shadow-indigo-200">
            <UserPlus className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Zero Trust Dispatch</h1>
          <p className="text-slate-500 mt-2 text-center text-sm">{t('auth.register_title')}</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">{t('auth.email')}</label>
            <Input 
              type="email" 
              placeholder="admin@yourcompany.com" 
              className="h-11" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">{t('auth.password')}</label>
            <Input 
              type="password" 
              placeholder={t('auth.password_placeholder')}
              className="h-11" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
              minLength={8}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700 flex items-center gap-1.5">
              <Building2 className="w-4 h-4 text-slate-400" />
              {t('auth.org_id_label')}
            </label>
            <Input 
              type="text" 
              placeholder={t('auth.org_id_placeholder')}
              className="h-11 font-mono text-sm bg-slate-50" 
              value={orgId}
              onChange={(e) => setOrgId(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
              required 
              pattern="^[a-z0-9_]+$"
              title={t('auth.org_id_validation')}
            />
            <p className="text-[11px] text-slate-400">{t('auth.org_id_hint')}</p>
          </div>

          <div className="flex items-start space-x-2 pt-2">
            <input 
              type="checkbox" 
              id="terms" 
              className="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-600"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              required
            />
            <label htmlFor="terms" className="text-xs text-slate-500 leading-tight">
              {t('auth.terms_agreement')}
            </label>
          </div>

          {errorMsg && (
            <div className="p-3 bg-red-50 rounded-md border border-red-100 flex items-start space-x-2">
              <Lock className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
              <p className="text-sm text-red-600 leading-tight">{errorMsg}</p>
            </div>
          )}

          <Button type="submit" className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 mt-6 transition-colors shadow-md shadow-indigo-200" disabled={loading || !agreed}>
            {loading ? (
              <><Loader2 className="animate-spin w-5 h-5 mr-2" /> {t('auth.registering')}</>
            ) : (
              <><ShieldCheck className="w-5 h-5 mr-2" /> {t('auth.register_btn')}</>
            )}
          </Button>

          <div className="text-center pt-5 mt-2 border-t border-slate-100 text-sm text-slate-600">
            {t('auth.has_account')} <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-medium ml-1">{t('auth.login')}</Link>
          </div>
        </form>

        <div className="mt-8 flex justify-center items-center gap-2 text-slate-400 text-sm">
          <Lock className="w-4 h-4" />
          <span>{t('auth.data_isolated')}</span>
        </div>
      </div>
    </div>
  );
};
