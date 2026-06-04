import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Shield, Key, Building, Loader2, KeyRound, Bot, Copy, Plus, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '@/api/client';
import { useTranslation } from 'react-i18next';

export const SettingsTab = () => {
  const { t } = useTranslation();
  const user = useAuthStore((state) => state.user);
  
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error(t('auth.passwords_do_not_match', 'Нові паролі не співпадають'));
      return;
    }
    
    // Client-side validation for the new policy
    const passRegex = /^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;
    if (!passRegex.test(passwordData.newPassword)) {
      toast.error(t('auth.password_complexity_error', 'Пароль має містити мінімум 8 символів, цифру та спецсимвол'));
      return;
    }

    setIsChangingPassword(true);
    try {
      // The backend endpoint the user is going to build
      await apiClient.put('/auth/password', {
        old_password: passwordData.oldPassword,
        new_password: passwordData.newPassword
      });
      toast.success(t('auth.password_changed_success', 'Пароль успішно змінено'));
      setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const err = error as any;
      toast.error(err.response?.data?.detail || t('auth.error_generic', 'Помилка при зміні пароля'));
    } finally {
      setIsChangingPassword(false);
    }
  };

  const [apiKeys, setApiKeys] = useState<{id: string, key: string, created_at: string}[]>([]);
  const [isGeneratingKey, setIsGeneratingKey] = useState(false);
  
  const [systemPrompt, setSystemPrompt] = useState('');
  const [isSavingPrompt, setIsSavingPrompt] = useState(false);
  const [isLoadingSettings, setIsLoadingSettings] = useState(true);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const [keysRes, promptRes] = await Promise.all([
          apiClient.get('/settings/apikeys'),
          apiClient.get('/settings/prompt')
        ]);
        setApiKeys(keysRes.data);
        if (promptRes.data.system_prompt) {
          setSystemPrompt(promptRes.data.system_prompt);
        }
      } catch (err) {
        console.error("Failed to load settings", err);
      } finally {
        setIsLoadingSettings(false);
      }
    };
    fetchSettings();
  }, []);

  const handleGenerateKey = async () => {
    setIsGeneratingKey(true);
    try {
      const res = await apiClient.post('/settings/apikeys');
      setApiKeys([res.data, ...apiKeys]);
      toast.success('Новий API ключ успішно згенеровано');
    } catch {
      toast.error('Помилка генерації ключа');
    } finally {
      setIsGeneratingKey(false);
    }
  };

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key);
    toast.success('Ключ скопійовано в буфер обміну');
  };

  const handleDeleteKey = async (id: string) => {
    try {
      await apiClient.delete(`/settings/apikeys/${id}`);
      setApiKeys(apiKeys.filter(k => k.id !== id));
      toast.success('Ключ успішно видалено');
    } catch {
      toast.error('Помилка видалення ключа');
    }
  };

  const maskApiKey = (key: string) => {
    if (key.length < 20) return key;
    return key.slice(0, 12) + '...' + key.slice(-6);
  };

  const handleSavePrompt = async () => {
    setIsSavingPrompt(true);
    try {
      await apiClient.put('/settings/prompt', { system_prompt: systemPrompt });
      toast.success('Системний промпт успішно збережено');
    } catch {
      toast.error('Помилка збереження промпту');
    } finally {
      setIsSavingPrompt(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h2 className="text-2xl font-semibold mb-6 text-white">{t('dashboard.settings_tab.title', 'Налаштування')}</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Profile & Security Card */}
        <Card className="bg-[#09090b]/80 border-slate-800/60 backdrop-blur-md shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
          <CardHeader>
            <CardTitle className="flex items-center text-slate-100">
              <Shield className="w-5 h-5 mr-2 text-indigo-400" />
              Профіль та Безпека
            </CardTitle>
            <CardDescription className="text-slate-400">
              Управління доступом та зміна пароля
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* User Info */}
            <div className="flex items-center p-4 bg-slate-900/50 rounded-lg border border-slate-800">
              <Building className="w-5 h-5 mr-4 text-slate-500" />
              <div>
                <p className="text-sm font-medium text-slate-300">Організація (Тенант)</p>
                <p className="text-xs text-slate-500 font-mono mt-1">{user?.organizationId}</p>
              </div>
            </div>

            <div className="flex items-center p-4 bg-slate-900/50 rounded-lg border border-slate-800">
              <Shield className="w-5 h-5 mr-4 text-slate-500" />
              <div>
                <p className="text-sm font-medium text-slate-300">Роль користувача</p>
                <p className="text-xs text-slate-500 uppercase mt-1">{user?.role}</p>
              </div>
            </div>

            {/* Change Password Form */}
            <form onSubmit={handlePasswordChange} className="space-y-4 pt-4 border-t border-slate-800/60">
              <h4 className="text-sm font-medium text-slate-200">Зміна пароля</h4>
              <div className="space-y-2">
                <Label htmlFor="old_password">Поточний пароль</Label>
                <Input 
                  id="old_password" 
                  type="password" 
                  value={passwordData.oldPassword}
                  onChange={(e) => setPasswordData({...passwordData, oldPassword: e.target.value})}
                  className="bg-slate-900 border-slate-800 text-slate-200" 
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="new_password">Новий пароль</Label>
                  <Input 
                    id="new_password" 
                    type="password" 
                    value={passwordData.newPassword}
                    onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                    className="bg-slate-900 border-slate-800 text-slate-200" 
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Підтвердження</Label>
                  <Input 
                    id="confirm_password" 
                    type="password" 
                    value={passwordData.confirmPassword}
                    onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                    className="bg-slate-900 border-slate-800 text-slate-200" 
                    required
                  />
                </div>
              </div>
              <Button type="submit" disabled={isChangingPassword} className="w-full bg-indigo-600 hover:bg-indigo-500 text-white mt-2">
                {isChangingPassword ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Key className="w-4 h-4 mr-2" />}
                Оновити пароль
              </Button>
            </form>

          </CardContent>
        </Card>

        <div className="space-y-6">
          
          <Card className="bg-[#09090b]/80 border-slate-800/60 backdrop-blur-md shadow-xl opacity-100 transition-opacity">
            <CardHeader>
              <CardTitle className="flex items-center text-slate-100">
                <KeyRound className="w-5 h-5 mr-2 text-emerald-400" />
                API Ключі (Інтеграція)
              </CardTitle>
              <CardDescription className="text-slate-400">
                Згенеруйте API-ключ для віджета на вашому сайті
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {isLoadingSettings ? (
                  <div className="flex justify-center p-4"><Loader2 className="w-6 h-6 animate-spin text-slate-500" /></div>
                ) : (
                  <>
                    {apiKeys.length === 0 ? (
                       <div className="p-8 text-center border border-dashed border-slate-700 rounded-lg">
                         <p className="text-sm text-slate-500 mb-4">У вас ще немає згенерованих API ключів.</p>
                       </div>
                    ) : (
                      <div className="space-y-3">
                        {apiKeys.map((k) => (
                          <div key={k.id} className="flex items-center justify-between p-3 bg-slate-900/80 rounded-md border border-slate-700/50">
                            <div className="flex items-center">
                               <Key className="w-4 h-4 mr-3 text-slate-500" />
                               <code className="text-emerald-400 text-sm">{maskApiKey(k.key)}</code>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Button variant="ghost" size="icon" onClick={() => handleCopyKey(k.key)} className="h-8 w-8 text-slate-400 hover:text-white" title="Скопіювати">
                                 <Copy className="w-4 h-4" />
                              </Button>
                              <Button variant="ghost" size="icon" onClick={() => handleDeleteKey(k.id)} className="h-8 w-8 text-slate-400 hover:text-red-400" title="Видалити">
                                 <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    <Button onClick={handleGenerateKey} disabled={isGeneratingKey} className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 mt-2">
                      {isGeneratingKey ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
                      Згенерувати новий ключ
                    </Button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-[#09090b]/80 border-slate-800/60 backdrop-blur-md shadow-xl opacity-100 transition-opacity">
            <CardHeader>
              <CardTitle className="flex items-center text-slate-100">
                <Bot className="w-5 h-5 mr-2 text-amber-400" />
                Параметри ШІ (System Prompt)
              </CardTitle>
              <CardDescription className="text-slate-400">
                Налаштуйте специфічні бізнес-правила для ШІ-диспетчера
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                 <textarea 
                    value={systemPrompt}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setSystemPrompt(e.target.value)}
                    placeholder="Наприклад: Ми працюємо тільки з рефрижераторами. Ніколи не погоджуйтесь на тентові перевезення."
                    className="min-h-[120px] w-full p-3 rounded-md bg-slate-900 border border-slate-800 text-slate-200 resize-none focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-amber-500/30"
                 />
                 <Button onClick={handleSavePrompt} disabled={isSavingPrompt || isLoadingSettings} className="w-full bg-amber-600 hover:bg-amber-500 text-white">
                   {isSavingPrompt ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                   Зберегти правила
                 </Button>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
};
