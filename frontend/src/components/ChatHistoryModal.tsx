import { useState, useRef, useEffect } from 'react';
import { format } from 'date-fns';
import { uk, enUS, pl } from 'date-fns/locale';
import { Loader2, Send } from 'lucide-react';
import DOMPurify from 'dompurify';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { useChatHistory, useSendMessage } from '@/hooks/useHistory';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';
import type { Locale } from 'date-fns';

interface ChatHistoryModalProps {
  sessionId: string | null;
  isOpen: boolean;
  onClose: () => void;
  isHumanControlled?: boolean;
}

const locales: Record<string, Locale> = { uk, en: enUS, pl };

export const ChatHistoryModal = ({ sessionId, isOpen, onClose, isHumanControlled = false }: ChatHistoryModalProps) => {
  const { data: history, isLoading, isError } = useChatHistory(sessionId);
  const sendMessageMutation = useSendMessage();
  const [message, setMessage] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const { t, i18n } = useTranslation();

  const currentLocale = locales[i18n.language] || enUS;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !sessionId) return;

    sendMessageMutation.mutate({ sessionId, message });
    setMessage('');
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl bg-slate-950 border-slate-800 text-slate-200 flex flex-col max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="text-xl text-slate-100 flex items-center justify-between pr-6">
            <span>
              {t('chat.history')} <span className="text-slate-500 font-mono text-sm ml-2">{sessionId}</span>
            </span>
            {isHumanControlled && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900/40 text-blue-400 border border-blue-800">
                {t('chat.human_controlled')}
              </span>
            )}
          </DialogTitle>
          <DialogDescription className="sr-only">{t('chat.history_desc')}</DialogDescription>
        </DialogHeader>

        <div className="mt-4 flex-1 overflow-hidden flex flex-col">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin mb-4 text-blue-500" />
            </div>
          ) : isError ? (
            <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-400 text-center">
              <p>{t('chat.error_loading')}</p>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto pr-4 mb-4 min-h-[300px] custom-scrollbar">
              <div className="flex flex-col space-y-4 pb-4">
                {history?.length === 0 ? (
                  <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
                    {t('chat.history_desc')}
                  </div>
                ) : (
                  history?.map((msg, index) => {
                    const isManual = msg.role === 'assistant' && msg.text.includes('[MANUAL_OPERATOR]');
                    const rawText = isManual ? msg.text.replace('[MANUAL_OPERATOR]', '') : msg.text;
                    const cleanText = DOMPurify.sanitize(rawText);
                    const isUser = msg.role === 'user';
                    
                    return (
                      <div
                        key={index}
                        className={`flex flex-col max-w-[80%] rounded-xl p-4 ${
                          isUser
                            ? 'bg-blue-600 text-white self-end rounded-tr-sm'
                            : isManual
                              ? 'bg-indigo-600/90 text-white self-end rounded-tr-sm border border-indigo-500' // Диспетчер
                              : 'bg-slate-800 text-slate-200 self-start rounded-tl-sm border border-slate-700' // ШІ
                        }`}
                      >
                        <div className="text-sm opacity-70 mb-1 flex justify-between items-center">
                          <span className="font-semibold uppercase tracking-wider text-[10px]">
                            {isUser ? 'Client' : (isManual ? t('dashboard.dispatcher') : 'AI')}
                          </span>
                          <span className="text-[10px] ml-4">
                            {format(new Date(msg.timestamp), 'p', { locale: currentLocale })}
                          </span>
                        </div>
                        <p className="whitespace-pre-wrap text-sm leading-relaxed">{cleanText}</p>
                      </div>
                    );
                  })
                )}
                <div ref={scrollRef} />
              </div>
            </div>
          )}

          {isHumanControlled && (
            <form onSubmit={handleSend} className="flex gap-2 pt-2 border-t border-slate-800 mt-auto">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={t('chat.type_message')}
                className="bg-slate-900 border-slate-700 text-slate-200 focus-visible:ring-blue-500"
                disabled={sendMessageMutation.isPending}
              />
              <Button 
                type="submit" 
                disabled={sendMessageMutation.isPending || !message.trim()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8"
              >
                {sendMessageMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </form>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
