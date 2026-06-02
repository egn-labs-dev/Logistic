import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import { toast } from 'sonner';

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
  return useMutation({
    mutationFn: (session_id: string) => apiClient.post('/dispatcher/intercept', { session_id }),
    onSuccess: (_, session_id) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success(`Сесію ${session_id} успішно перехоплено. ШІ вимкнено.`);
    },
    onError: () => {
      toast.error('Помилка при перехопленні чату. Спробуйте ще раз.');
    }
  });
};
