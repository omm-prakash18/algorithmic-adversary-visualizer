import React from 'react';
import { Skull, AlertCircle, CheckCircle2, Search, Zap, Target } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  feedback: string;
  edgeCase: string;
  injectionDetected: boolean;
  isLoading: boolean;
}

const AdversaryPanel: React.FC<Props> = ({ feedback, edgeCase, injectionDetected, isLoading }) => {
  return (
    <div className="flex flex-col h-full bg-[#020617]/90 backdrop-blur-2xl border border-white/5 rounded-3xl overflow-hidden shadow-2xl relative group">
      {/* Glossy Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent pointer-events-none" />
      
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="p-1 bg-red-500/20 rounded-md border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
            <Skull size={12} className="text-red-500" />
          </div>
          <div className="flex flex-col">
            <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest leading-none mb-0.5">Red-Team Analysis</span>
            <span className="text-[11px] font-bold text-red-400 font-mono tracking-tighter uppercase">Adversarial Tutor v1.0</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
           <div className={`w-1 h-1 rounded-full ${isLoading ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'} shadow-[0_0_8px_currentColor]`} />
           <span className="text-[8px] font-mono text-slate-500 uppercase tracking-tighter">{isLoading ? 'Processing' : 'Standby'}</span>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-4 space-y-4 overflow-y-auto scrollbar-none relative">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div 
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-full space-y-4"
            >
              <div className="relative">
                <Search size={32} className="text-red-500 animate-bounce" />
                <motion.div 
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                  className="absolute inset-0 border-t-2 border-red-500 rounded-full"
                />
              </div>
              <div className="text-[10px] font-mono text-red-500/50 uppercase tracking-[0.3em]">Scanning Logic Flows...</div>
            </motion.div>
          ) : (
            <motion.div 
              key="content"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Feedback Section */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                   <Target size={12} className="text-slate-600" />
                   <label className="text-[9px] text-slate-500 uppercase font-black tracking-widest">Intelligence Report</label>
                </div>
                <div className="p-4 bg-white/5 rounded-2xl border border-white/5 shadow-inner">
                  <p className="text-[13px] text-slate-200 font-medium italic leading-relaxed">
                    {feedback ? `"${feedback}"` : "Submit your synchronization sequence. I am scanning for vulnerabilities."}
                  </p>
                </div>
              </div>
              
              {/* Edge Case Section */}
              {edgeCase && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                     <Zap size={12} className="text-amber-500" />
                     <label className="text-[9px] text-slate-500 uppercase font-black tracking-widest">Vulnerability Trigger</label>
                  </div>
                  <div className="p-4 bg-slate-950 rounded-2xl border border-amber-500/20 font-mono text-[13px] text-amber-400 shadow-[inset_0_0_20px_rgba(245,158,11,0.05)]">
                    {edgeCase}
                  </div>
                </div>
              )}

              {/* Status Indicators */}
              <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {injectionDetected ? (
                    <div className="flex items-center gap-2 px-3 py-1 bg-red-500/10 rounded-full border border-red-500/20">
                      <AlertCircle size={14} className="text-red-500" />
                      <span className="text-[10px] text-red-400 font-bold uppercase tracking-tight">Injection Detected</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                      <CheckCircle2 size={14} className="text-emerald-500" />
                      <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-tight">Logic Verified</span>
                    </div>
                  )}
                </div>
                <div className="text-[9px] font-mono text-slate-700 italic uppercase">Vector-Core Active</div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default AdversaryPanel;
