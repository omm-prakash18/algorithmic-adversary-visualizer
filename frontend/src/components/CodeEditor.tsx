import React from 'react';
import { Play, ShieldAlert, FileCode, Terminal } from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  code: string;
  setCode: (code: string) => void;
  onExecute: () => void;
  onAttack: () => void;
  isLoading: boolean;
}

const CodeEditor: React.FC<Props> = ({ code, setCode, onExecute, onAttack, isLoading }) => {
  const lineCount = code.split('\n').length;

  return (
    <div className="flex flex-col h-full bg-[#0d1117]/80 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden shadow-[0_20px_50px_rgba(0,0,0,0.5),inset_0_0_20px_rgba(59,130,246,0.05)] group transition-all hover:border-blue-500/30">
      {/* Editor Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="p-1 bg-blue-500/20 rounded-md border border-blue-500/30">
            <FileCode size={12} className="text-blue-400" />
          </div>
          <div className="flex flex-col">
            <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest leading-none mb-0.5">Source Logic</span>
            <span className="text-[11px] font-bold text-slate-200 font-mono tracking-tight">main_algorithm.cpp</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onExecute}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-600 text-white text-[10px] font-black uppercase tracking-widest rounded-xl transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)] border border-blue-400/20"
          >
            <Play size={12} className="fill-current" />
            Synchronize
          </motion.button>
          
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onAttack}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-1.5 bg-red-600/20 hover:bg-red-600/30 disabled:bg-slate-800 disabled:text-slate-600 text-red-500 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all border border-red-500/30"
          >
            <ShieldAlert size={12} />
            Scan
          </motion.button>
        </div>
      </div>

      {/* Editor Content */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Line Numbers */}
        <div className="w-12 bg-black/20 border-r border-white/5 py-4 flex flex-col items-center select-none">
          {Array.from({ length: Math.max(lineCount, 20) }).map((_, i) => (
            <div key={i} className="text-[10px] font-mono text-slate-600 h-6 leading-6">
              {(i + 1).toString().padStart(2, '0')}
            </div>
          ))}
        </div>

        {/* Text Area */}
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          spellCheck={false}
          className="flex-1 p-4 bg-transparent text-blue-100 font-mono text-[13px] leading-6 outline-none resize-none scrollbar-none selection:bg-blue-500/30"
          placeholder="#include <iostream>..."
        />
        
        {/* Visual Decoration */}
        <div className="absolute bottom-4 right-6 opacity-5 pointer-events-none">
          <Terminal size={120} className="text-blue-500" />
        </div>
      </div>
      
      {/* Footer Info */}
      <div className="px-6 py-2 bg-black/20 border-t border-white/5 flex items-center justify-between">
        <div className="flex gap-4">
           <span className="text-[9px] font-mono text-slate-600 uppercase">UTF-8</span>
           <span className="text-[9px] font-mono text-slate-600 uppercase">C++17</span>
        </div>
        <div className="text-[9px] font-mono text-blue-500/50 uppercase tracking-widest animate-pulse">
           Live Kernel Link Active
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;
