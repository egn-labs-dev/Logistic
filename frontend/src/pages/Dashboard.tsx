import { useEffect, useState } from 'react';
import { useAlerts, useIntercept } from '@/hooks/useAlerts';
import { useAnalytics } from '@/hooks/useAnalytics';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useAuthStore } from '@/store/authStore';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { 
  LogOut, ShieldAlert, Loader2, History, Activity, 
  BrainCircuit, Clock, Wallet, LayoutDashboard, Settings, BellRing, MessageSquareWarning,
  MapPin, Truck, Weight, ThermometerSnowflake, FileJson
} from 'lucide-react';
import { toast } from 'sonner';
import { ChatHistoryModal } from '@/components/ChatHistoryModal';
import { EfficiencyChart } from '@/components/EfficiencyChart';
import { SettingsTab } from '@/components/SettingsTab';
import { cn } from '@/lib/utils';

import { ALERT_SOUND } from '@/assets/alertSound';

export const Dashboard = () => {
  const { t } = useTranslation();
  const setToken = useAuthStore((state) => state.setToken);
  const { data: alerts, isLoading: isAlertsLoading } = useAlerts();
  const { data: stats, isLoading: isStatsLoading } = useAnalytics();
  const interceptMutation = useIntercept();

  const [historySessionId, setHistorySessionId] = useState<string | null>(null);
  const [activeNav, setActiveNav] = useState('overview');

  const handleLogout = () => {
    setToken(null);
  };

  const [previousAlertCount, setPreviousAlertCount] = useState(0);

  useEffect(() => {
    if (alerts) {
      const activeIncidents = alerts.filter((a: any) => a.status === 'human_required').length;
      
      if (activeIncidents > previousAlertCount) {
        // Play alert sound
        try {
          const audio = new Audio(ALERT_SOUND);
          audio.volume = 0.5;
          const playPromise = audio.play();
          
          if (playPromise !== undefined) {
            playPromise.catch(error => {
              console.log("Browser autoplay policy blocked the sound. User needs to interact with the page first.", error);
            });
          }
        } catch (e) {
          console.error("Audio playback failed", e);
        }

        toast.error(`${t('dashboard.live_feed.active')}: ${activeIncidents} (НОВИЙ ІНЦИДЕНТ!)`, {
          id: 'alerts-toast-new',
        });
      }
      setPreviousAlertCount(activeIncidents);
    }
  }, [alerts, previousAlertCount, t]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30">
      
      {/* SIDEBAR */}
      <aside className="hidden md:flex w-64 flex-col border-r border-slate-800/40 bg-slate-950/50 backdrop-blur-2xl z-20 shadow-2xl">
        <div className="flex h-16 items-center px-6 border-b border-slate-800/60">
          <div className="bg-indigo-600/20 p-1.5 rounded-lg mr-3 shadow-[0_0_15px_rgba(79,70,229,0.3)]">
            <ShieldAlert className="w-5 h-5 text-indigo-400" />
          </div>
          <span className="font-semibold tracking-tight text-white">ZT Dispatch</span>
        </div>
        
        <div className="flex-1 overflow-y-auto py-6 px-4">
          <nav className="space-y-1.5">
            <button 
              onClick={() => setActiveNav('overview')}
              className={cn(
                "w-full flex items-center px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200",
                activeNav === 'overview' 
                  ? "bg-indigo-500/10 text-indigo-400" 
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
              )}
            >
              <LayoutDashboard className="w-4 h-4 mr-3" />
              {t('dashboard.title')}
            </button>
            <button 
              onClick={() => setActiveNav('alerts')}
              className={cn(
                "w-full flex items-center px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200 relative",
                activeNav === 'alerts' 
                  ? "bg-indigo-500/10 text-indigo-400" 
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
              )}
            >
              <BellRing className="w-4 h-4 mr-3" />
              {t('dashboard.alerts')}
              {alerts && alerts.length > 0 && (
                <span className="absolute right-3 flex h-5 w-5 items-center justify-center rounded-full bg-red-500/20 text-red-500 text-[10px] font-bold border border-red-500/30">
                  {alerts.length}
                </span>
              )}
            </button>
            <button 
              onClick={() => setActiveNav('settings')}
              className={cn(
                "w-full flex items-center px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200",
                activeNav === 'settings' 
                  ? "bg-indigo-500/10 text-indigo-400" 
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
              )}
            >
              <Settings className="w-4 h-4 mr-3" />
              {t('dashboard.settings')}
            </button>
          </nav>
        </div>

        <div className="p-4 border-t border-slate-800/60">
          <div className="flex items-center p-3 rounded-xl bg-slate-900/50 border border-slate-800 mb-4">
            <div className="h-8 w-8 rounded-full bg-indigo-900 flex items-center justify-center mr-3 border border-indigo-700/50">
              <span className="text-xs font-bold text-indigo-200">DP</span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-slate-200 leading-none">{t('dashboard.dispatcher')}</span>
              <span className="text-[10px] text-emerald-400 mt-1 flex items-center">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                {t('dashboard.online')}
              </span>
            </div>
          </div>
          <Button 
            variant="ghost" 
            onClick={handleLogout} 
            className="w-full justify-start text-slate-400 hover:text-white hover:bg-red-500/10 hover:text-red-400 transition-colors"
          >
            <LogOut className="w-4 h-4 mr-3" />
            {t('dashboard.logout')}
          </Button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-slate-950">
        
        {/* Top Navbar Mobile + Status */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800/60 backdrop-blur-md sticky top-0 z-10">
          <div className="md:hidden flex items-center">
             <ShieldAlert className="w-5 h-5 text-indigo-400 mr-2" />
             <span className="font-semibold text-white">ZT Dispatch</span>
          </div>
          <div className="hidden md:flex">
             <h2 className="text-lg font-medium text-slate-200">{t('dashboard.operations_overview')}</h2>
          </div>
          
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <div className="text-xs text-slate-400 flex items-center bg-slate-900/80 px-3 py-1.5 rounded-full border border-slate-800 shadow-inner">
              <span className="relative flex h-2 w-2 mr-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
              </span>
              {t('dashboard.data_synced')}
            </div>
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeNav === 'overview' && (
            <div className="max-w-7xl mx-auto space-y-6">
            
            {/* KPI GRID */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="bg-slate-950/40 border-slate-800/40 backdrop-blur-md hover:bg-slate-900/60 transition-all duration-300 shadow-lg hover:shadow-indigo-500/5 group">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium text-slate-400 group-hover:text-slate-300 transition-colors">{t('dashboard.kpi.autonomy_rate')}</span>
                    <div className="bg-blue-500/10 p-2 rounded-md">
                      <BrainCircuit className="h-4 w-4 text-blue-400" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-slate-100 tracking-tight">
                    {isStatsLoading ? <Loader2 className="w-6 h-6 animate-spin text-slate-600" /> : `${stats?.autonomy_rate ?? 0}%`}
                  </div>
                  <div className="mt-2 text-xs text-emerald-400 flex items-center">
                    <span className="mr-1">↗</span> {t('dashboard.kpi.growing_trust')}
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-slate-950/40 border-slate-800/40 backdrop-blur-md hover:bg-slate-900/60 transition-all duration-300 shadow-lg hover:shadow-indigo-500/5 group">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium text-slate-400 group-hover:text-slate-300 transition-colors">{t('dashboard.kpi.response_time')}</span>
                    <div className="bg-emerald-500/10 p-2 rounded-md">
                      <Clock className="h-4 w-4 text-emerald-400" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-slate-100 tracking-tight">
                    {isStatsLoading ? <Loader2 className="w-6 h-6 animate-spin text-slate-600" /> : (stats?.hitl_response_time || "0s")}
                  </div>
                  <div className="mt-2 text-xs text-slate-500">{t('dashboard.kpi.avg_dispatcher_time')}</div>
                </CardContent>
              </Card>

              <Card className="bg-slate-950/40 border-slate-800/40 backdrop-blur-md hover:bg-slate-900/60 transition-all duration-300 shadow-lg hover:shadow-indigo-500/5 group">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium text-slate-400 group-hover:text-slate-300 transition-colors">{t('dashboard.kpi.active_incidents')}</span>
                    <div className="bg-red-500/10 p-2 rounded-md">
                      <Activity className="h-4 w-4 text-red-400" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-white tracking-tight flex items-baseline gap-2">
                    {isAlertsLoading ? <Loader2 className="w-6 h-6 animate-spin text-slate-600" /> : (alerts?.filter((a: { status: string }) => a.status === 'human_required')?.length || 0)}
                    {(alerts?.filter((a: { status: string }) => a.status === 'human_required')?.length || 0) > 0 && (
                       <span className="text-xs font-normal text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/20">{t('dashboard.kpi.attention')}</span>
                    )}
                  </div>
                  <div className="mt-2 text-xs text-slate-500">{t('dashboard.kpi.needs_intervention')}</div>
                </CardContent>
              </Card>

              <Card className="bg-slate-950/40 border-slate-800/40 backdrop-blur-md hover:bg-slate-900/60 transition-all duration-300 shadow-lg hover:shadow-indigo-500/5 group">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium text-slate-400 group-hover:text-slate-300 transition-colors">{t('dashboard.kpi.savings')}</span>
                    <div className="bg-amber-500/10 p-2 rounded-md">
                      <Wallet className="h-4 w-4 text-amber-400" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-slate-100 tracking-tight">
                    {isStatsLoading ? <Loader2 className="w-6 h-6 animate-spin text-slate-600" /> : `${stats?.cost_savings_hours ?? 0}`}
                  </div>
                  <div className="mt-2 text-xs text-amber-400/80 flex items-center">
                    <span className="mr-1">{t('dashboard.kpi.saved_by_ai')}</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* MAIN DASHBOARD SPLIT (2/3 Chart, 1/3 Live Feed) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Analytics Chart (Takes 2 columns) */}
              <Card className="lg:col-span-2 bg-slate-950/40 border-slate-800/40 backdrop-blur-md flex flex-col shadow-lg">
                <div className="p-5 border-b border-slate-800/40 flex justify-between items-center bg-slate-900/20">
                  <div>
                    <h3 className="font-semibold text-slate-100">{t('dashboard.chart.title')}</h3>
                    <p className="text-xs text-slate-400 mt-1">{t('dashboard.chart.subtitle')}</p>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-medium">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
                      <span className="text-slate-300">{t('dashboard.chart.autonomous')}</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-amber-500 mr-2"></div>
                      <span className="text-slate-300">{t('dashboard.chart.dispatcher')}</span>
                    </div>
                  </div>
                </div>
                <div className="p-5 flex-1 min-h-[400px]">
                  {isStatsLoading ? (
                    <div className="h-full w-full flex items-center justify-center">
                      <Loader2 className="w-8 h-8 animate-spin text-slate-700" />
                    </div>
                  ) : stats?.chart_data ? (
                    <EfficiencyChart data={stats.chart_data} />
                  ) : (
                    <div className="h-full w-full flex items-center justify-center text-slate-500 text-sm">
                      {t('dashboard.chart.no_data')}
                    </div>
                  )}
                </div>
              </Card>

              {/* Live Alerts Feed (Takes 1 column) */}
              <Card className="bg-slate-950/40 border-slate-800/40 backdrop-blur-md flex flex-col shadow-lg overflow-hidden relative">
                <div className="p-5 border-b border-slate-800/40 flex justify-between items-center bg-slate-900/30">
                  <div className="flex items-center">
                    <div className="relative flex h-2 w-2 mr-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                    </div>
                    <h3 className="font-semibold text-slate-100">{t('dashboard.live_feed.title')}</h3>
                  </div>
                  <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-full font-medium border border-slate-700">
                    {alerts?.length || 0} {t('dashboard.live_feed.active')}
                  </span>
                </div>
                
                <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
                  {isAlertsLoading ? (
                    <div className="flex justify-center p-8">
                      <Loader2 className="w-6 h-6 animate-spin text-slate-700" />
                    </div>
                  ) : alerts?.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-48 text-center px-4">
                      <div className="bg-slate-900 rounded-full p-4 mb-3 border border-slate-800">
                         <ShieldAlert className="w-6 h-6 text-slate-600" />
                      </div>
                      <p className="text-sm font-medium text-slate-300">{t('dashboard.live_feed.no_incidents')}</p>
                      <p className="text-xs text-slate-500 mt-1">{t('dashboard.live_feed.ai_working')}</p>
                    </div>
                  ) : (
                    alerts?.map((alert: { id: string, session_id: string, status: string }) => {
                      const isControlled = alert.status === 'human_controlled';
                      return (
                        <div 
                          key={alert.id} 
                          className={cn(
                            "p-4 rounded-xl border transition-all duration-300 animate-slide-up",
                            isControlled 
                              ? "bg-slate-900/30 border-indigo-500/20 hover:bg-slate-900/50 hover:border-indigo-500/40" 
                              : "bg-slate-900/40 border-red-500/30 hover:bg-slate-900/80 hover:border-red-500/50 animate-pulse-glow"
                          )}
                        >
                          
                          <div className="pl-1">
                            <div className="flex justify-between items-start mb-2">
                              <span className="font-mono text-xs text-slate-400 truncate w-3/4">
                                {alert.session_id}
                              </span>
                              <span className={cn(
                                "text-[9px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wide",
                                isControlled ? "text-indigo-400 bg-indigo-500/10" : "text-red-400 bg-red-500/10 animate-pulse"
                              )}>
                                {isControlled ? t('dashboard.live_feed.under_control') : t('dashboard.live_feed.sos')}
                              </span>
                            </div>
                            
                            <p className="text-xs text-slate-400 mb-4 line-clamp-2">
                              {isControlled ? t('dashboard.live_feed.you_control') : t('dashboard.live_feed.ai_blocked')}
                            </p>
                            
                            <div className="flex space-x-2">
                              {!isControlled && (
                                <Button 
                                  size="sm"
                                  onClick={() => interceptMutation.mutate(alert.session_id)}
                                  disabled={interceptMutation.isPending}
                                  className="flex-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 h-8 text-xs font-medium border border-red-500/20 transition-colors"
                                >
                                  {interceptMutation.isPending && interceptMutation.variables === alert.session_id ? (
                                    <Loader2 className="w-3 h-3 mr-1.5 animate-spin" />
                                  ) : null}
                                  {t('dashboard.live_feed.intercept')}
                                </Button>
                              )}
                              <Button
                                variant={isControlled ? "default" : "outline"}
                                size="sm"
                                onClick={() => setHistorySessionId(alert.session_id)}
                                className={cn(
                                  "h-8 text-xs font-medium transition-colors",
                                  isControlled 
                                    ? "flex-1 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/20" 
                                    : "px-3 bg-slate-900/40 border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white"
                                )}
                              >
                                {isControlled ? (
                                  <><MessageSquareWarning className="w-3 h-3 mr-1.5" /> {t('dashboard.live_feed.open_chat')}</>
                                ) : (
                                  <History className="w-3 h-3" />
                                )}
                              </Button>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </Card>
              
            </div>
            </div>
          )}

          {activeNav === 'alerts' && (
            <div className="max-w-7xl mx-auto space-y-6">
               <h2 className="text-2xl font-semibold mb-6 text-white">{t('dashboard.alerts_tab.title')}</h2>
               {alerts && alerts.length > 0 ? (
                 <div className="grid gap-4">
                   {alerts.map((alert: { id: string, session_id: string, status: string, cargo_details?: any }) => {
                     const isSecurityThreat = alert.cargo_details && alert.cargo_details.error;
                     
                     return (
                       <div key={alert.id} className="bg-slate-900/40 border border-slate-800/50 rounded-xl p-5 flex flex-col hover:bg-slate-900/60 transition-colors shadow-sm gap-4">
                         <div className="flex justify-between items-center w-full border-b border-slate-800/30 pb-3">
                           <div>
                             <div className="font-mono text-sm text-slate-300 mb-1">{alert.session_id}</div>
                             <div className="text-xs text-slate-500">
                               Статус: <span className={cn(
                                 "font-medium px-2 py-0.5 rounded-full ml-1",
                                 alert.status === 'human_controlled' ? "bg-indigo-500/10 text-indigo-400" : "bg-red-500/10 text-red-400"
                               )}>
                                 {alert.status === 'human_controlled' ? t('dashboard.live_feed.under_control') : t('dashboard.live_feed.sos')}
                               </span>
                             </div>
                           </div>
                           <Button
                             variant="outline"
                             size="sm"
                             onClick={() => setHistorySessionId(alert.session_id)}
                             className="bg-slate-900/40 border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
                           >
                             <History className="w-4 h-4 mr-2" />
                             Переглянути чат
                           </Button>
                         </div>
                         
                         {/* Відображення деталей заявки */}
                         {alert.cargo_details && (
                           <div className="w-full">
                             {isSecurityThreat ? (
                               <div className="bg-amber-500/10 rounded-lg p-4 border border-amber-500/30 w-full flex flex-col shadow-sm">
                                 <div className="text-xs font-semibold mb-4 uppercase tracking-wide flex items-center text-amber-500">
                                   <ShieldAlert className="w-4 h-4 mr-1.5" /> ЗАГРОЗА БЕЗПЕЦІ (ПЕРЕХОПЛЕНО)
                                 </div>
                                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                   <div className="bg-amber-950/40 rounded-md p-3 border border-amber-500/20">
                                     <div className="text-[10px] text-amber-500/70 uppercase font-semibold mb-1">Тип загрози</div>
                                     <div className="text-sm font-medium text-amber-400 flex items-center">
                                       {alert.cargo_details.error || 'Невідома загроза'}
                                     </div>
                                   </div>
                                   <div className="bg-amber-950/40 rounded-md p-3 border border-amber-500/20">
                                     <div className="text-[10px] text-amber-500/70 uppercase font-semibold mb-1">Перехоплений текст (Payload)</div>
                                     <div className="text-xs font-mono text-amber-400/80 italic break-words">
                                       "{alert.cargo_details.raw_input || 'Немає даних'}"
                                     </div>
                                   </div>
                                 </div>
                               </div>
                             ) : (
                               <div className="flex flex-col space-y-4">
                                 <div className="flex items-center justify-between">
                                   <div className="text-xs font-semibold uppercase tracking-wide flex items-center text-emerald-500">
                                     <FileJson className="w-4 h-4 mr-1.5" /> ДАНІ ГОТОВІ ДЛЯ TMS
                                   </div>
                                 </div>
                                 
                                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                   {/* Route details */}
                                   <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800">
                                     <div className="flex items-start">
                                       <MapPin className="w-5 h-5 text-indigo-400 mt-0.5 mr-3 shrink-0" />
                                       <div>
                                         <div className="text-[10px] text-slate-500 uppercase font-semibold mb-1">Маршрут</div>
                                         <div className="text-sm font-medium text-slate-200">
                                           {alert.cargo_details.departure_city || 'Не вказано'} 
                                           <span className="text-slate-600 mx-2">→</span> 
                                           {alert.cargo_details.destination_city || 'Не вказано'}
                                         </div>
                                       </div>
                                     </div>
                                   </div>

                                   {/* Cargo & Weight */}
                                   <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800 flex justify-between">
                                     <div className="flex items-start">
                                       <Truck className="w-5 h-5 text-blue-400 mt-0.5 mr-3 shrink-0" />
                                       <div>
                                         <div className="text-[10px] text-slate-500 uppercase font-semibold mb-1">Вантаж</div>
                                         <div className="text-sm font-medium text-slate-200 capitalize">
                                           {alert.cargo_details.cargo_type || 'Не вказано'}
                                         </div>
                                         {alert.cargo_details.body_type_required && (
                                           <div className="text-xs text-slate-400 mt-1 capitalize">
                                             Кузов: {alert.cargo_details.body_type_required}
                                           </div>
                                         )}
                                       </div>
                                     </div>
                                     {alert.cargo_details.weight_tons && (
                                       <div className="flex items-start border-l border-slate-800 pl-4 ml-2">
                                         <div>
                                           <div className="text-[10px] text-slate-500 uppercase font-semibold mb-1 text-right">Вага</div>
                                           <div className="text-sm font-bold text-slate-200 flex items-center justify-end">
                                             <Weight className="w-3.5 h-3.5 mr-1 text-slate-400" />
                                             {alert.cargo_details.weight_tons} т
                                           </div>
                                         </div>
                                       </div>
                                     )}
                                   </div>

                                   {/* Temperature */}
                                   {alert.cargo_details.temperature_control?.is_required && (
                                     <div className="bg-blue-900/20 rounded-lg p-4 border border-blue-500/20 md:col-span-2">
                                       <div className="flex items-center">
                                         <div className="p-1.5 bg-blue-500/20 rounded-md mr-3">
                                           <ThermometerSnowflake className="w-4 h-4 text-blue-400" />
                                         </div>
                                         <div>
                                           <div className="text-[10px] text-blue-400/70 uppercase font-semibold">Температурний режим</div>
                                           <div className="text-sm font-medium text-blue-300">
                                             {alert.cargo_details.temperature_control.min_temp_celsius !== undefined ? `Від ${alert.cargo_details.temperature_control.min_temp_celsius}°C ` : ''}
                                             {alert.cargo_details.temperature_control.max_temp_celsius !== undefined ? `до ${alert.cargo_details.temperature_control.max_temp_celsius}°C` : ''}
                                           </div>
                                         </div>
                                       </div>
                                     </div>
                                   )}
                                 </div>
                               </div>
                             )}
                           </div>
                         )}
                       </div>
                     );
                   })}
                 </div>
               ) : (
                 <div className="bg-slate-900/30 border border-slate-800/40 rounded-xl p-12 flex flex-col items-center justify-center text-center text-slate-500">
                    <BellRing className="w-12 h-12 mb-4 text-slate-600" />
                    <p className="text-lg font-medium text-slate-300">Інцидентів немає</p>
                    <p className="text-sm mt-2 max-w-md">Всі сесії обробляються автономно</p>
                 </div>
               )}
            </div>
          )}

          {activeNav === 'settings' && (
            <SettingsTab />
          )}
        </div>
      </main>

      <ChatHistoryModal 
        sessionId={historySessionId}
        isOpen={!!historySessionId}
        onClose={() => setHistorySessionId(null)}
        isHumanControlled={alerts?.find((a: { session_id: string, status: string }) => a.session_id === historySessionId)?.status === 'human_controlled'}
      />
    </div>
  );
};
