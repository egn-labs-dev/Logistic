import { useEffect, useState } from 'react';
import { useAlerts, useIntercept } from '@/hooks/useAlerts';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useAuthStore } from '@/store/authStore';
import { LogOut, ShieldAlert, Loader2, MessageSquareWarning, History } from 'lucide-react';
import { toast } from 'sonner';
import { ChatHistoryModal } from '@/components/ChatHistoryModal';

export const Dashboard = () => {
  const setToken = useAuthStore((state) => state.setToken);
  const { data: alerts, isLoading, isError, error } = useAlerts();
  const interceptMutation = useIntercept();

  const [historySessionId, setHistorySessionId] = useState<string | null>(null);

  const handleLogout = () => {
    setToken(null);
  };

  // Сповіщення при появі нових алертів
  useEffect(() => {
    if (alerts && alerts.length > 0) {
      toast.error(`Увага! ${alerts.length} вантаж(ів) потребують ручного втручання!`, {
        id: 'alerts-toast', // запобігає дублюванню тостів
      });
    }
  }, [alerts?.length]);

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

      <main className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold flex items-center">
            <MessageSquareWarning className="w-5 h-5 mr-2 text-orange-400" />
            Активні інциденти
          </h2>
          <div className="text-sm text-slate-500 flex items-center">
            <span className="relative flex h-3 w-3 mr-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            Live (syncing...)
          </div>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin mb-4 text-blue-500" />
            <p>Завантаження алертів...</p>
          </div>
        ) : isError ? (
          <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-400 text-center">
            <p>Помилка завантаження даних.</p>
            <p className="text-sm opacity-80">{(error as any)?.message}</p>
          </div>
        ) : alerts?.length === 0 ? (
          <div className="p-12 border border-dashed border-slate-800 rounded-xl flex flex-col items-center justify-center text-center bg-slate-900/50">
            <ShieldAlert className="w-16 h-16 text-slate-700 mb-4" />
            <h3 className="text-xl font-semibold text-slate-300">Все спокійно</h3>
            <p className="text-slate-500 max-w-md mt-2">
              Немає активних чатів, які потребують перехоплення. ШІ повністю справляється з поточним навантаженням.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {alerts.map((alert: any) => (
              <Card key={alert.id} className="p-5 flex justify-between items-center bg-slate-900/80 border-red-900/50 shadow-lg shadow-red-900/10">
                <div>
                  <p className="text-sm text-slate-400 mb-1">ID Сесії</p>
                  <p className="font-mono text-lg text-slate-200">{alert.session_id}</p>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-900/40 text-red-400 mt-2 border border-red-800">
                    Human Required
                  </span>
                </div>
                <div className="flex space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => setHistorySessionId(alert.session_id)}
                    className="border-slate-700 hover:bg-slate-800 text-slate-300"
                  >
                    <History className="w-4 h-4 mr-2" />
                    Переглянути історію
                  </Button>
                  <Button 
                    onClick={() => interceptMutation.mutate(alert.session_id)}
                    disabled={interceptMutation.isPending}
                    className="bg-red-600 hover:bg-red-700 text-white"
                  >
                    {interceptMutation.isPending && interceptMutation.variables === alert.session_id ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : null}
                    Перехопити контроль
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
      
      {/* Модальне вікно історії чату */}
      <ChatHistoryModal 
        sessionId={historySessionId}
        isOpen={!!historySessionId}
        onClose={() => setHistorySessionId(null)}
      />
    </div>
  );
};
