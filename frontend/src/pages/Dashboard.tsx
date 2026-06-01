
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { LogOut, ShieldAlert } from 'lucide-react';

export const Dashboard = () => {
  const setToken = useAuthStore((state) => state.setToken);

  const handleLogout = () => {
    setToken(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <header className="flex justify-between items-center mb-10 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center">
            <ShieldAlert className="w-8 h-8 mr-3 text-red-500" />
            HITL Console
          </h1>
          <p className="text-slate-400 mt-1">Огляд запитів, що потребують втручання диспетчера</p>
        </div>
        <Button variant="outline" onClick={handleLogout} className="border-slate-700 hover:bg-slate-800 text-slate-300">
          <LogOut className="w-4 h-4 mr-2" />
          Вийти
        </Button>
      </header>

      <main>
        <div className="p-12 border border-dashed border-slate-800 rounded-xl flex flex-col items-center justify-center text-center bg-slate-900/50">
          <ShieldAlert className="w-16 h-16 text-slate-700 mb-4" />
          <h2 className="text-xl font-semibold text-slate-300">Дашборд у розробці</h2>
          <p className="text-slate-500 max-w-md mt-2">
            Авторизація успішна. Наступним кроком ми виведемо тут реал-тайм таблицю алертів (статуси human_required) та підключимо TanStack Query.
          </p>
        </div>
      </main>
    </div>
  );
};
