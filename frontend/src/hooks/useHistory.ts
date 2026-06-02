import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';

export interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export const useChatHistory = (sessionId: string | null) => {
  return useQuery<ChatMessage[]>({
    queryKey: ['history', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const res = await apiClient.get(`/dispatcher/history/${sessionId}`);
      return res.data;
    },
    enabled: !!sessionId,
    refetchInterval: sessionId ? 3000 : false, // Polling for "live" chat
  });
};

export const useSendMessage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, message }: { sessionId: string; message: string }) => 
      apiClient.post('/dispatcher/send', { session_id: sessionId, message }),
    onSuccess: (_, { sessionId }) => {
      // Update history immediately after sending
      queryClient.invalidateQueries({ queryKey: ['history', sessionId] });
    }
  });
};
