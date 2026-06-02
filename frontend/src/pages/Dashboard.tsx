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
  BrainCircuit, Clock, Wallet, LayoutDashboard, Settings, BellRing, MessageSquareWarning
} from 'lucide-react';
import { toast } from 'sonner';
import { ChatHistoryModal } from '@/components/ChatHistoryModal';
import { EfficiencyChart } from '@/components/EfficiencyChart';
import { cn } from '@/lib/utils';

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

  useEffect(() => {
    if (alerts && alerts.length > 0) {
      toast.error(`${t('dashboard.live_feed.active')}: ${alerts.length}`, {
        id: 'alerts-toast',
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [alerts?.length]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#09090b] text-slate-100 font-sans selection:bg-indigo-500/30">
      
      {/* SIDEBAR */}
      <aside className="hidden md:flex w-64 flex-col border-r border-slate-800/60 bg-[#09090b]/80 backdrop-blur-xl z-20">
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
      <main className="flex-1 flex flex-col relative overflow-hidden bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900/15 via-[#09090b] to-[#09090b]">
        
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
              <Card className="bg-[#09090b]/60 border-slate-800/60 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300 hover:shadow-[0_0_20px_rgba(79,70,229,0.05)] group">
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
              
              <Card className="bg-[#09090b]/60 border-slate-800/60 backdrop-blur-sm hover:border-emerald-500/30 transition-all duration-300 hover:shadow-[0_0_20px_rgba(16,185,129,0.05)] group">
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

              <Card className="bg-[#09090b]/60 border-slate-800/60 backdrop-blur-sm hover:border-red-500/30 transition-all duration-300 hover:shadow-[0_0_20px_rgba(239,68,68,0.05)] group">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium text-slate-400 group-hover:text-slate-300 transition-colors">{t('dashboard.kpi.active_incidents')}</span>
                    <div className="bg-red-500/10 p-2 rounded-md">
                      <Activity className="h-4 w-4 text-red-400" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-white tracking-tight flex items-baseline gap-2">
                    {isAlertsLoading ? <Loader2 className="w-6 h-6 animate-spin text-slate-600" /> : alerts?.filter((a: { status: string }) => a.status === 'human_required').length || 0}
                    {alerts?.filter((a: { status: string }) => a.status === 'human_required').length > 0 && (
                       <span className="text-xs font-normal text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/20 animate-pulse">{t('dashboard.kpi.attention')}</span>
                    )}
                  </div>
                  <div className="mt-2 text-xs text-slate-500">{t('dashboard.kpi.needs_intervention')}</div>
                </CardContent>
              </Card>

              <Card className="bg-[#09090b]/60 border-slate-800/60 backdrop-blur-sm hover:border-amber-500/30 transition-all duration-300 hover:shadow-[0_0_20px_rgba(245,158,11,0.05)] group">
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
              <Card className="lg:col-span-2 bg-[#09090b]/80 border-slate-800/60 backdrop-blur-md flex flex-col shadow-xl">
                <div className="p-5 border-b border-slate-800/40 flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold text-slate-100">{t('dashboard.chart.title')}</h3>
                    <p className="text-xs text-slate-400 mt-1">{t('dashboard.chart.subtitle')}</p>
                  </div>
                  <div className="flex items-center gap-4 text-xs font-medium">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mr-2 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></div>
                      <span className="text-slate-300">{t('dashboard.chart.autonomous')}</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-amber-500 mr-2 shadow-[0_0_8px_rgba(245,158,11,0.8)]"></div>
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
              <Card className="bg-[#09090b]/80 border-slate-800/60 backdrop-blur-md flex flex-col shadow-xl overflow-hidden">
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
                            "p-4 rounded-xl border relative overflow-hidden transition-all duration-300 group hover:shadow-lg",
                            isControlled 
                              ? "bg-indigo-950/20 border-indigo-900/50 hover:bg-indigo-900/30" 
                              : "bg-red-950/20 border-red-900/50 hover:bg-red-900/30"
                          )}
                        >
                          {/* Accent Gradient Border Effect */}
                          <div className={cn(
                            "absolute top-0 left-0 w-1 h-full",
                            isControlled ? "bg-indigo-500" : "bg-red-500"
                          )}></div>
                          
                          <div className="pl-2">
                            <div className="flex justify-between items-start mb-2">
                              <span className="font-mono text-xs text-slate-300 truncate w-3/4">
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
                                  className="flex-1 bg-red-600/90 hover:bg-red-500 text-white h-8 text-xs font-medium shadow-[0_0_10px_rgba(220,38,38,0.3)] hover:shadow-[0_0_15px_rgba(220,38,38,0.5)] transition-all border border-red-500"
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
                                    ? "flex-1 bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_10px_rgba(79,70,229,0.3)]" 
                                    : "px-3 bg-slate-900/80 border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white"
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
               <div className="bg-[#09090b]/60 border border-slate-800/60 rounded-xl p-12 flex flex-col items-center justify-center text-center text-slate-500">
                  <BellRing className="w-12 h-12 mb-4 text-slate-700" />
                  <p className="text-lg text-slate-300">{t('dashboard.alerts_tab.subtitle')}</p>
                  <p className="text-sm mt-2 max-w-md">{t('dashboard.alerts_tab.description')}</p>
               </div>
            </div>
          )}

          {activeNav === 'settings' && (
            <div className="max-w-7xl mx-auto space-y-6">
               <h2 className="text-2xl font-semibold mb-6 text-white">{t('dashboard.settings_tab.title')}</h2>
               <div className="bg-[#09090b]/60 border border-slate-800/60 rounded-xl p-12 flex flex-col items-center justify-center text-center text-slate-500">
                  <Settings className="w-12 h-12 mb-4 text-slate-700" />
                  <p className="text-lg text-slate-300">{t('dashboard.settings_tab.subtitle')}</p>
                  <p className="text-sm mt-2 max-w-md">{t('dashboard.settings_tab.description')}</p>
               </div>
            </div>
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
