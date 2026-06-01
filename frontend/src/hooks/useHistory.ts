import { useQuery } from '@tanstack/react-query';
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
    enabled: !!sessionId, // Хук запускає запит тільки якщо передано session_id
  });
};
