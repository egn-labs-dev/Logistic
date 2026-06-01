import { format } from 'date-fns';
import { Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useChatHistory } from '@/hooks/useHistory';

interface ChatHistoryModalProps {
  sessionId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ChatHistoryModal = ({ sessionId, isOpen, onClose }: ChatHistoryModalProps) => {
  const { data: history, isLoading, isError } = useChatHistory(sessionId);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl bg-slate-950 border-slate-800 text-slate-200">
        <DialogHeader>
          <DialogTitle className="text-xl text-slate-100">
            Історія діалогу <span className="text-slate-500 font-mono text-sm ml-2">{sessionId}</span>
          </DialogTitle>
        </DialogHeader>

        <div className="mt-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin mb-4 text-blue-500" />
              <p>Завантаження та де-анонімізація даних...</p>
            </div>
          ) : isError ? (
            <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-400 text-center">
              <p>Не вдалося завантажити історію чату.</p>
            </div>
          ) : history?.length === 0 ? (
            <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-lg">
              Історія діалогу порожня.
            </div>
          ) : (
            <ScrollArea className="h-[500px] pr-4">
              <div className="flex flex-col space-y-4">
                {history?.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex flex-col max-w-[80%] rounded-xl p-4 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white self-end rounded-tr-sm'
                        : 'bg-slate-800 text-slate-200 self-start rounded-tl-sm border border-slate-700'
                    }`}
                  >
                    <div className="text-sm opacity-70 mb-1 flex justify-between items-center">
                      <span className="font-semibold uppercase tracking-wider text-[10px]">
                        {msg.role === 'user' ? 'Клієнт' : 'ШІ'}
                      </span>
                      <span className="text-[10px] ml-4">
                        {format(new Date(msg.timestamp), 'HH:mm:ss')}
                      </span>
                    </div>
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.text}</p>
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
