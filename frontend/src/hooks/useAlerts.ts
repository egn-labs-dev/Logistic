import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../api/client';
import { toast } from 'sonner';
import { useTranslation } from 'react-i18next';

import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/store/authStore';

// Типізація для нашого алерта
export interface Alert {
    id: string;
    session_id: string;
    status: string;
    driver_id: string;
    created_at?: string;
    message_preview?: string;
    cargo_details?: any;
}

// Функція для генерації "Enterprise" звуку оповіщення без аудіофайлів
const playAlertSound = () => {
    try {
        const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContext) return;
        
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, ctx.currentTime); // Тон A5
        gain.gain.setValueAtTime(0.1, ctx.currentTime); // Гучність 10%
        
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + 0.5); // Плавне затухання за 0.5с
        osc.stop(ctx.currentTime + 0.5);
    } catch (e) {
        console.error('Помилка відтворення звуку:', e);
    }
};

export const useAlerts = () => {
    const queryClient = useQueryClient();
    const token = useAuthStore((state: any) => state.token);
    const wsRef = useRef<WebSocket | null>(null);

    // 1. Початкове завантаження (БЕЗ refetchInterval!)
    const query = useQuery<Alert[]>({
        queryKey: ['alerts'],
        queryFn: async () => {
            const { data } = await apiClient.get('/dispatcher/alerts');
            return data;
        },
    });

    // 2. Управління WebSocket з'єднанням
    useEffect(() => {
        if (!token) return;

        // Динамічне визначення URL сокета (wss для https, ws для http)
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Якщо є VITE_WS_URL, використовуємо його, інакше беремо поточний хост
        const wsHost = import.meta.env.VITE_WS_URL || `${wsProtocol}//${window.location.host}`;
        const wsUrl = `${wsHost}/ws/alerts?token=${token}`;

        const connectWs = () => {
            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('✅ WebSocket підключено до Zero Trust Dispatch');
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'NEW_ALERT') {
                        playAlertSound();
                        
                        toast.error('🚨 Новий інцидент! Потрібен диспетчер.', {
                            description: `Водій: ${data.payload.driver_id}`,
                            duration: 5000,
                        });

                        // Миттєве оновлення кешу React Query
                        queryClient.setQueryData<Alert[]>(['alerts'], (oldData) => {
                            const currentData = oldData || [];
                            // Захист від дублікатів
                            if (currentData.some(a => a.id === data.payload.session_id)) {
                                return currentData;
                            }
                            
                            // Додаємо новий алерт на початок списку
                            return [{
                                id: data.payload.session_id,
                                session_id: data.payload.session_id,
                                status: data.payload.status,
                                driver_id: data.payload.driver_id,
                                message_preview: data.payload.message_preview,
                                created_at: new Date().toISOString()
                            }, ...currentData];
                        });
                    }

                    if (data.type === 'STATUS_UPDATE') {
                        // Якщо статус "перехоплено" або "закрито" — прибираємо його зі стрічки активних алертів
                        if (['resolved_won', 'resolved_lost', 'human_controlled'].includes(data.payload.status)) {
                            queryClient.setQueryData<Alert[]>(['alerts'], (oldData) => {
                                if (!oldData) return [];
                                return oldData.filter(a => a.id !== data.payload.session_id);
                            });
                        } else {
                            // Інакше просто оновлюємо статус існуючого
                            queryClient.setQueryData<Alert[]>(['alerts'], (oldData) => {
                                if (!oldData) return [];
                                return oldData.map(a => 
                                    a.id === data.payload.session_id 
                                        ? { ...a, status: data.payload.status } 
                                        : a
                                );
                            });
                        }
                    }
                } catch (err) {
                    console.error('Помилка парсингу WS повідомлення:', err);
                }
            };

            ws.onclose = () => {
                console.warn('❌ WebSocket відключено. Перепідключення через 3 сек...');
                setTimeout(connectWs, 3000);
            };
            
            ws.onerror = (error) => {
                console.error('Помилка WebSocket:', error);
                ws.close(); // Форсуємо закриття для тригера onclose
            };
        };

        connectWs();

        // Очищення при розмонтуванні компонента
        return () => {
            if (wsRef.current) {
                wsRef.current.onclose = null; // Запобігаємо нескінченному циклу реконектів
                wsRef.current.close();
            }
        };
    }, [token, queryClient]);

    return query;
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
