import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Lock, LogIn, Truck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import apiClient from '@/api/client';
import { useAuthStore } from '@/store/authStore';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const setToken = useAuthStore((state) => state.setToken);
  const navigate = useNavigate();

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
    } catch (error: any) {
      if (error.response?.status === 401 || error.response?.status === 400) {
        setErrorMsg('Невірні дані або доступ до системи призупинено.');
      } else {
        setErrorMsg('Виникла помилка при з\'єднанні з сервером. Спробуйте пізніше.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <Card className="w-full max-w-md bg-slate-950/50 border-slate-800 text-slate-100 backdrop-blur-xl shadow-2xl">
        <CardHeader className="space-y-3 pb-6">
          <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-2 shadow-lg shadow-blue-500/20">
            <Truck className="text-white w-6 h-6" />
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight">Zero Trust Dispatch</CardTitle>
          <CardDescription className="text-slate-400">
            Введіть ваші облікові дані для доступу до HITL консолі.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-300">Робочий Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="dispatcher@cargo.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-slate-900 border-slate-700 text-slate-200 placeholder:text-slate-500 focus-visible:ring-blue-500"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-300">Пароль доступу</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-slate-900 border-slate-700 text-slate-200 focus-visible:ring-blue-500"
              />
            </div>

            {errorMsg && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-md flex items-start space-x-2">
                <Lock className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <p className="text-sm text-red-400 leading-tight">{errorMsg}</p>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-md hover:shadow-blue-600/25 mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Перевірка...
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4 mr-2" />
                  Увійти в систему
                </>
              )}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center border-t border-slate-800/60 pt-4 pb-2">
          <p className="text-xs text-slate-500 flex items-center">
            <Lock className="w-3 h-3 mr-1" />
            З'єднання зашифровано
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};
