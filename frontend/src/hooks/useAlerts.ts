import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import { toast } from 'sonner';
import { useTranslation } from 'react-i18next';

export const useAlerts = () => {
  return useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await apiClient.get('/dispatcher/alerts');
      return res.data;
    },
    refetchInterval: 5000, // Real-time polling every 5 seconds
  });
};

export const useIntercept = () => {
  const queryClient = useQueryClient();
  const { t } = useTranslation();
  
  return useMutation({
    mutationFn: (session_id: string) => apiClient.post('/dispatcher/intercept', { session_id }),
    onSuccess: (_, session_id) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success(t('alerts.intercept_success') + ` (${session_id})`);
    },
    onError: () => {
      toast.error(t('alerts.intercept_error'));
    }
  });
};
