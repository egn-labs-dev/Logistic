import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';

export interface AnalyticsStats {
  autonomy_rate: number;
  hitl_response_time: string;
  active_incidents: number;
  cost_savings_hours: number;
  chart_data: Array<{
    day: string;
    autonomous: number;
    manual: number;
  }>;
}

export const useAnalytics = () => {
  return useQuery<AnalyticsStats>({
    queryKey: ['analyticsStats'],
    queryFn: async () => {
      const response = await apiClient.get('/dispatcher/stats');
      return response.data;
    },
    refetchInterval: 15000, // Refresh stats every 15 seconds
  });
};
