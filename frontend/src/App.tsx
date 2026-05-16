import React, { useState, useEffect } from 'react';
import CodeEditor from './components/CodeEditor';
import AlgorithmVisualizer from './components/AlgorithmVisualizer';
import AdversaryPanel from './components/AdversaryPanel';
import { CyberArtifact } from './components/CyberArtifact';
import api from './api';
import { Terminal, Activity, ShieldCheck, Zap, Command, LayoutGrid, BarChart3, GripVertical, GripHorizontal } from 'lucide-react';
import { motion } from 'framer-motion';
import ErrorBoundary from './components/ErrorBoundary';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';

const DEFAULT_CODE = `#include <iostream>
#include <vector>

struct Node {
    int val;
    Node *left, *right;
    Node(int v) : val(v), left(NULL), right(NULL) {}
};

// Neural Insertion Logic
Node* insert(Node* root, int val) {
    if (!root) return new Node(val);
    if (val < root->val) root->left = insert(root->left, val);
    else root->right = insert(root->right, val);
    return root;
}

int main() {
    std::vector<int> inputs = {10, 5, 15, 3, 7};
    Node* root = NULL;
    for (int x : inputs) {
        root = insert(root, x);
    }
    std::cout << "BST SYNCHRONIZATION COMPLETE." << std::endl;
    return 0;
}`;

const CustomResizeHandle = ({ direction = 'vertical' }: { direction?: 'vertical' | 'horizontal' }) => (
  <PanelResizeHandle className={`group relative flex items-center justify-center bg-transparent transition-colors hover:bg-blue-500/10 ${direction === 'horizontal' ? 'w-full h-2' : 'h-full w-2'}`}>
    <div className={`bg-white/5 rounded-full flex items-center justify-center transition-all group-hover:bg-blue-500/20 ${direction === 'horizontal' ? 'w-16 h-1' : 'h-16 w-1'}`}>
      {direction === 'horizontal' ? <GripHorizontal size={8} className="text-slate-600 group-hover:text-blue-400" /> : <GripVertical size={8} className="text-slate-600 group-hover:text-blue-400" />}
    </div>
  </PanelResizeHandle>
);

function App() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [steps, setSteps] = useState([]);
  const [feedback, setFeedback] = useState('');
  const [edgeCase, setEdgeCase] = useState('');
  const [injectionDetected, setInjectionDetected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [stdout, setStdout] = useState('');
  const [isInitializing, setIsInitializing] = useState(true);
  const [systemStatus, setSystemStatus] = useState('OFFLINE');

  useEffect(() => {
    const initSystem = async () => {
      try {
        await api.get('');
        setSystemStatus('STABLE');
      } catch (err) {
        setSystemStatus('SIGNAL_LOSS');
      } finally {
        setTimeout(() => setIsInitializing(false), 1500);
      }
    };
    initSystem();
  }, []);


  const handleExecute = async () => {
    setIsLoading(true);
    setStdout('KINETIC LINK ESTABLISHED. EXECUTING...');
    try {
      const execRes = await api.post('sandbox/execute/', { user_code: code });
      let output = execRes.data.status === 'success' || execRes.data.status === 'mock_success' 
        ? execRes.data.stdout 
        : `SIGNAL LOSS: ${execRes.data.stderr || execRes.data.error}`;
      setStdout(output);

      const visualRes = await api.post('visualize/generate-steps/', { user_code: code });
      setSteps(visualRes.data.steps || []);
    } catch (err: any) {
      setStdout(`CRITICAL FAILURE: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAttack = async () => {
    setIsLoading(true);
    try {
      const res = await api.post('adversary/attack/', { problem_type: 'BST', user_code: code });
      setFeedback(res.data.adversary_feedback);
      setEdgeCase(res.data.edge_case_input);
      setInjectionDetected(res.data.injection_attempt_detected);
    } catch (err: any) {
      setFeedback('THE ADVERSARY IS SHROUDED.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isInitializing) {
    return (
      <div className="h-screen w-screen bg-[#020617] flex flex-col items-center justify-center font-mono relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:40px_40px] opacity-10 animate-pulse" />
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="z-10 text-center"
        >
          <div className="text-blue-500 text-5xl font-black mb-6 tracking-tighter drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]">
            ADVERSARY-SYS
          </div>
          <div className="w-80 h-1.5 bg-slate-900 border border-white/5 rounded-full overflow-hidden mx-auto shadow-inner text-white">
            <motion.div 
               animate={{ x: ['-100%', '100%'] }}
               transition={{ repeat: Infinity, duration: 1.2, ease: 'easeInOut' }}
               className="h-full w-full bg-gradient-to-r from-transparent via-blue-500 to-transparent"
            />
          </div>
          <div className="text-slate-500 text-[10px] mt-6 uppercase tracking-[0.4em] font-bold">
            Synchronizing Neural Matrix...
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-[#070B14] text-slate-300 font-sans selection:bg-blue-500/30 overflow-hidden relative">
      <div className="vignette-grid" />

      {/* Cinematic Header */}
      <header className="z-10 flex items-center justify-between px-10 py-5 bg-slate-900/20 backdrop-blur-2xl border-b border-white/5 shadow-[0_10px_40px_rgba(0,0,0,0.4)]">
        <div className="flex items-center gap-6">
          <motion.div 
            whileHover={{ scale: 1.1, rotate: 90 }}
            className="p-3 bg-blue-600 rounded-2xl glow-blue cursor-pointer"
          >
            <Zap size={24} className="text-white fill-white" />
          </motion.div>
          <div>
            <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
              ADVERSARY <span className="bg-blue-600/20 text-blue-500 px-2 py-0.5 rounded-md text-[10px] font-mono border border-blue-500/20 uppercase tracking-widest">v4.0-CORE</span>
            </h1>
            <div className="flex items-center gap-2 mt-1">
              <span className={`h-1.5 w-1.5 rounded-full animate-pulse shadow-[0_0_8px_currentColor] ${systemStatus === 'STABLE' ? 'bg-emerald-500 text-emerald-500' : 'bg-red-500 text-red-500'}`} />
              <span className="text-[9px] text-slate-500 uppercase font-black tracking-[0.2em]">
                {systemStatus === 'STABLE' ? 'Neural Trace Synchronized' : 'Neural Uplink Offline'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-10">
           <nav className="flex items-center gap-6">
              {[
                { icon: LayoutGrid, label: 'Visualizer' },
                { icon: BarChart3, label: 'Analytics' },
                { icon: ShieldCheck, label: 'Red-Team' }
              ].map((item, i) => (
                <button key={i} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
                   <item.icon size={14} />
                   <span className="text-[10px] font-bold uppercase tracking-widest">{item.label}</span>
                </button>
              ))}
           </nav>
           
           <div className="h-12 w-[1px] bg-white/10" />
           
           <div className="flex items-center gap-4 text-white">
              <div className="flex flex-col items-end">
                 <span className="text-[8px] text-slate-500 uppercase font-black tracking-widest leading-none mb-1">System Load</span>
                 <span className="text-[11px] text-blue-400 font-mono font-bold tracking-tighter uppercase font-mono">Optimal-8001</span>
              </div>
              <div className="w-16 h-16 opacity-90">
                 <CyberArtifact />
              </div>
           </div>
        </div>
      </header>

      {/* Main Container with Resizable Panels */}
      <main className="z-10 flex-1 p-8 overflow-hidden">
        <PanelGroup direction="horizontal" autoSaveId="workspace-layout-v1">
          {/* Left Column: Command & Input */}
          <Panel defaultSize={45} minSize={30}>
            <PanelGroup direction="vertical">
              <Panel defaultSize={70} minSize={20}>
                <div className="h-full glass-panel rounded-[2rem] overflow-hidden relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent pointer-events-none" />
                  <CodeEditor code={code} setCode={setCode} onExecute={handleExecute} onAttack={handleAttack} isLoading={isLoading} />
                </div>
              </Panel>
              
              <CustomResizeHandle direction="horizontal" />
              
              <Panel defaultSize={30} minSize={15}>
                <div className="h-full bg-[#020617]/90 backdrop-blur-2xl border border-white/5 rounded-[2rem] p-8 overflow-hidden relative shadow-inner group transition-all hover:border-blue-500/20">
                  <div className="absolute top-0 right-10 w-32 h-1 bg-gradient-to-r from-transparent via-blue-500/20 to-transparent blur-sm" />
                  <div className="flex items-center justify-between mb-5">
                    <div className="flex items-center gap-3 text-slate-400 font-black text-[10px] uppercase tracking-[0.3em]">
                      <Terminal size={14} className="text-blue-500" /> 
                      <span>Kernel Stream</span>
                    </div>
                    <div className="px-3 py-1 bg-blue-600/10 rounded text-[9px] text-blue-500 font-mono tracking-tighter uppercase">ROOT@SYS-CORE</div>
                  </div>
                  <div className="h-full overflow-y-auto scrollbar-none pb-6">
                    <pre className="text-sm font-mono text-blue-300/70 whitespace-pre-wrap leading-relaxed">
                      {stdout || '> WAITING FOR KERNEL INITIATION SEQUENCE...'}
                    </pre>
                  </div>
                </div>
              </Panel>
            </PanelGroup>
          </Panel>

          <CustomResizeHandle direction="vertical" />

          {/* Right Column: Visual & Intel */}
          <Panel defaultSize={55} minSize={30}>
            <PanelGroup direction="vertical">
              <Panel defaultSize={65} minSize={20}>
                <div className="h-full bg-slate-900/60 backdrop-blur-2xl rounded-[2.5rem] border border-white/5 overflow-hidden shadow-2xl relative group">
                   <div className="absolute -inset-[2px] bg-gradient-to-br from-indigo-500/10 via-transparent to-blue-500/10 rounded-[2.5rem] blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                   <AlgorithmVisualizer steps={steps} />
                </div>
              </Panel>
              
              <CustomResizeHandle direction="horizontal" />
              
              <Panel defaultSize={35} minSize={20}>
                <div className="h-full relative">
                   <AdversaryPanel feedback={feedback} edgeCase={edgeCase} injectionDetected={injectionDetected} isLoading={isLoading} />
                </div>
              </Panel>
            </PanelGroup>
          </Panel>
        </PanelGroup>
      </main>

      {/* Futuristic Footer Bar */}
      <footer className="z-10 px-10 py-3 bg-slate-950/95 backdrop-blur-3xl border-t border-white/5 flex items-center justify-between text-[10px] font-mono text-slate-500 uppercase tracking-[0.3em] font-bold">
        <div className="flex items-center gap-12">
          <div className="flex items-center gap-4">
             <div className="w-2.5 h-2.5 bg-blue-500 rounded-full shadow-[0_0_12px_rgba(59,130,246,0.6)] animate-pulse" />
             RAG-ENGINE: <span className="text-blue-400 font-black">CHROMA_PERSISTENT_v2</span>
          </div>
          <div className="flex items-center gap-4">
             <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full shadow-[0_0_12px_rgba(99,102,241,0.6)]" />
             SANDBOX: <span className="text-indigo-400 font-black">LINUX_KERNEL_LLVM</span>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-blue-500/50">ENC-PROTOCOL: XTS-AES-GCM</span>
          <span className="text-slate-800">|</span>
          <span className="text-slate-400 font-black tracking-normal italic uppercase">SYSTEM_ID: {Math.random().toString(36).substring(7).toUpperCase()}</span>
        </div>
      </footer>
    </div>
  );
}

export default function Root() {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  );
}
