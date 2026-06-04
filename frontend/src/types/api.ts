export interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export interface Alert {
  id: string;
  session_id: string;
  status: 'human_required' | 'human_controlled' | 'new' | 'active_chat' | 'qualified_lead';
}

export interface EfficiencyData {
  day: string;
  autonomous: number;
  manual: number;
}

export interface AnalyticsStats {
  autonomy_rate: number;
  hitl_response_time: string;
  active_incidents: number;
  cost_savings_hours: number;
  chart_data: EfficiencyData[];
}
