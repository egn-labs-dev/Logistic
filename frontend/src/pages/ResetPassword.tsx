import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { KeyRound, ArrowLeft, Loader2, ShieldAlert } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import apiClient from '@/api/client';
import { useTranslation } from 'react-i18next';
import { AxiosError } from 'axios';

export const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  const { t } = useTranslation();
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setErrorMsg(t('auth.passwords_dont_match'));
      return;
    }

    setLoading(true);
    setErrorMsg('');
    
    try {
      await apiClient.post('/auth/reset-password', { token, new_password: password });
      
      // Navigate to login after success
      navigate('/login', { state: { message: t('auth.password_changed') } });
    } catch (err: unknown) {
      if (err instanceof AxiosError && err.response) {
        setErrorMsg(t('auth.link_expired'));
      } else {
        setErrorMsg(t('auth.link_expired'));
      }
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="text-center">
          <ShieldAlert className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-900 mb-2">{t('auth.invalid_token_title')}</h2>
          <p className="text-slate-500 mb-6">{t('auth.invalid_token_desc')}</p>
          <Button asChild><Link to="/forgot-password">{t('auth.restore_password')}</Link></Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8">
        <div className="text-center mb-8">
          <div className="mx-auto w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-4">
            <KeyRound className="w-6 h-6 text-indigo-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">{t('auth.reset_password_title')}</h1>
          <p className="text-slate-500 text-sm">{t('auth.reset_password_desc')}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.new_password')}</label>
            <Input 
              type="password" 
              className="w-full h-11"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
              minLength={8}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.confirm_password')}</label>
            <Input 
              type="password" 
              className="w-full h-11"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required 
              minLength={8}
            />
          </div>

          {errorMsg && (
            <div className="p-3 bg-red-50 rounded-md border border-red-100 text-sm text-red-700">
              {errorMsg}
            </div>
          )}

          <Button type="submit" className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 mt-2" disabled={loading}>
            {loading ? <Loader2 className="animate-spin w-5 h-5" /> : t('auth.save_password')}
          </Button>
          
          <div className="text-center pt-4">
            <Link to="/login" className="text-sm text-slate-500 hover:text-indigo-600 font-medium inline-flex items-center">
              <ArrowLeft className="w-4 h-4 mr-1" /> {t('auth.cancel')}
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};
