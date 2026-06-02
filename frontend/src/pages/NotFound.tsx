import { Link } from 'react-router-dom';
import { FileQuestion, ShieldAlert, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const NotFound = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full max-w-4xl pointer-events-none">
        <div className="absolute top-[20%] left-[20%] w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-[20%] right-[20%] w-64 h-64 bg-red-500/5 rounded-full blur-3xl"></div>
      </div>

      <div className="w-full max-w-lg bg-white rounded-2xl shadow-xl border border-slate-100 p-10 relative z-10 flex flex-col items-center text-center">
        <div className="bg-slate-100 p-4 rounded-full mb-6">
          <FileQuestion className="w-12 h-12 text-slate-400" />
        </div>
        
        <h1 className="text-4xl font-extrabold text-slate-900 mb-2">404</h1>
        <h2 className="text-xl font-bold text-slate-800 mb-4">Сторінку не знайдено</h2>
        
        <p className="text-slate-500 mb-8 max-w-sm">
          Схоже, такої сторінки не існує. Можливо, посилання застаріло або сторінку було видалено політиками безпеки.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 w-full justify-center">
          <Button asChild variant="default" className="bg-indigo-600 hover:bg-indigo-700 h-11 px-8">
            <Link to="/">
              <ArrowLeft className="w-4 h-4 mr-2" /> Повернутися на Головну
            </Link>
          </Button>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-100 w-full flex items-center justify-center text-xs text-slate-400 font-medium">
          <ShieldAlert className="w-4 h-4 mr-1.5 text-slate-400" />
          Zero Trust Dispatch LLC. Access Logged.
        </div>
      </div>
    </div>
  );
};
