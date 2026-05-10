import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, { 
  Node, 
  Edge, 
  useNodesState, 
  useEdgesState,
  MarkerType 
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Info, Activity, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Step {
  step: number;
  action: string;
  node?: { id: number; value: number; role?: string };
  node_id?: number;
  parent_id?: number;
  source_id?: number;
  target_id?: number;
  value?: number;
  description: string;
  role?: string;
}

interface Props {
  steps: Step[];
}

const AlgorithmVisualizer: React.FC<Props> = ({ steps }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isBooting, setIsBooting] = useState(false);

  useEffect(() => {
    if (steps && steps.length > 0) {
       setIsBooting(true);
       setNodes([]);
       setEdges([]);
       setCurrentStep(0);
       const timer = setTimeout(() => setIsBooting(false), 1200);
       return () => clearTimeout(timer);
    } else {
       setNodes([]);
       setEdges([]);
       setCurrentStep(0);
    }
  }, [steps]);

  useEffect(() => {
    if (!steps || steps.length === 0 || currentStep >= steps.length || isBooting) {
      return;
    }

    const timer = setInterval(() => {
      processStep(steps[currentStep]);
      setCurrentStep(prev => prev + 1);
    }, 800);

    return () => clearInterval(timer);
  }, [steps, currentStep, isBooting]);

  const renderNodeLabel = (val: number, role?: string) => (
    <div className="flex flex-col items-center relative pointer-events-none select-none">
      {role && (
        <motion.span 
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute -top-7 whitespace-nowrap bg-blue-900/90 px-2 py-0.5 rounded-md border border-blue-500/50 text-blue-100 text-[8px] font-black uppercase tracking-[0.1em] shadow-[0_0_10px_rgba(59,130,246,0.3)] backdrop-blur-sm"
        >
          {role}
        </motion.span>
      )}
      <span className="text-[15px] font-black text-white drop-shadow-md">{val}</span>
    </div>
  );

  const processStep = (step: Step) => {
    if (!step) return;

    switch (step.action) {
      case 'create_root':
      case 'create_node':
        if (step.node) {
          setNodes(nds => {
            const isLinkedList = steps.some(s => s.action === 'link');
            const newPos = isLinkedList 
              ? { x: 80 + nds.length * 140, y: 150 }
              : { x: 350, y: 60 };
            
            return [...nds, {
              id: step.node!.id.toString(),
              data: { 
                label: renderNodeLabel(step.node!.value, step.node!.role || step.role),
                val: step.node!.value 
              },
              position: newPos,
              style: { 
                background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', 
                color: '#fff', 
                borderRadius: step.action === 'create_root' ? '50%' : '12px', 
                width: 50, 
                height: 50, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                border: '2px solid rgba(255,255,255,0.1)',
                boxShadow: '0 10px 25px rgba(29, 78, 216, 0.4), inset 0 0 10px rgba(255,255,255,0.2)',
              }
            }];
          });
        }
        break;

      case 'link':
        if (step.source_id !== undefined && step.target_id !== undefined) {
          setEdges(eds => [
            ...eds,
            {
              id: `e${step.source_id}-${step.target_id}`,
              source: step.source_id!.toString(),
              target: step.target_id!.toString(),
              animated: true,
              style: { stroke: '#475569', strokeWidth: 3 },
              markerEnd: { type: MarkerType.ArrowClosed, color: '#475569' }
            }
          ]);
        }
        break;

      case 'compare':
      case 'traverse':
        setNodes(nds => nds.map(node => {
          const nodeValue = node.data?.val;
          if (nodeValue === undefined) return node;
          
          const isTarget = node.id === (step.node_id ?? step.node?.id)?.toString();
          if (isTarget) {
            return { 
              ...node, 
              data: { ...node.data, label: renderNodeLabel(nodeValue, step.role || 'Tracing') },
              style: { 
                ...node.style, 
                background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)', 
                border: '2px solid rgba(255,255,255,0.2)', 
                scale: 1.15,
                boxShadow: '0 0 30px rgba(239, 68, 68, 0.6)',
                zIndex: 100
              } 
            };
          }
          return { 
            ...node, 
            data: { ...node.data, label: renderNodeLabel(nodeValue) },
            style: { 
              ...node.style, 
              background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', 
              border: '2px solid rgba(255,255,255,0.1)', 
              scale: 1,
              boxShadow: '0 10px 20px rgba(0,0,0,0.3)',
              zIndex: 1
            } 
          };
        }));
        break;

      case 'push':
        if (step.node) {
           setNodes(nds => [...nds, {
              id: step.node!.id.toString(),
              data: { label: renderNodeLabel(step.node!.value, 'Stacked'), val: step.node!.value },
              position: { x: 300, y: 400 - nds.length * 60 },
              style: { 
                background: 'linear-gradient(135deg, #10b981 0%, #047857 100%)', 
                color: '#fff', 
                borderRadius: '8px', 
                width: 120, 
                height: 45, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                boxShadow: '0 10px 20px rgba(16, 185, 129, 0.3)',
                border: '1px solid rgba(255,255,255,0.1)'
              }
           }]);
        }
        break;

      case 'pop':
        setNodes(nds => nds.slice(0, -1));
        break;

      case 'insert_left':
      case 'insert_right':
        if (step.node && (step.parent_id !== undefined || step.node_id !== undefined)) {
          const parentId = (step.parent_id ?? step.node_id)!.toString();
          
          setNodes(nds => {
            const parent = nds.find(n => n.id === parentId);
            if (!parent) return nds;

            const depth = Math.floor((parent.position.y - 60) / 110) + 1;
            const horizontalSpacing = 240 / Math.pow(1.85, depth);
            
            const xOffset = step.action === 'insert_left' ? -horizontalSpacing : horizontalSpacing;
            const newPos = { x: parent.position.x + xOffset, y: parent.position.y + 110 };
            
            const newNode = {
              id: step.node!.id.toString(),
              data: { label: renderNodeLabel(step.node!.value, step.role || 'New Leaf'), val: step.node!.value },
              position: newPos,
              style: { 
                background: 'linear-gradient(135deg, #10b981 0%, #047857 100%)', 
                color: '#fff', 
                borderRadius: '50%', 
                width: 50, 
                height: 50, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                border: '2px solid rgba(255,255,255,0.1)',
                boxShadow: '0 10px 25px rgba(16, 185, 129, 0.4)'
              }
            };

            return [
              ...nds.map(n => ({ 
                ...n, 
                data: { ...n.data, label: renderNodeLabel(n.data.val) }, 
                style: { ...n.style, background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', border: '2px solid rgba(255,255,255,0.1)', scale: 1, zIndex: 1 } 
              })),
              newNode
            ];
          });
          
          setEdges(eds => [
            ...eds,
            {
              id: `e${parentId}-${step.node!.id}`,
              source: parentId,
              target: step.node!.id.toString(),
              animated: true,
              style: { stroke: '#475569', strokeWidth: 3 },
              markerEnd: { type: MarkerType.ArrowClosed, color: '#475569' }
            }
          ]);
        }
        break;
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-[#0d1117]/60 backdrop-blur-xl rounded-[2.5rem] overflow-hidden relative border border-white/10 shadow-[0_30px_60px_rgba(0,0,0,0.6)]">
      {/* Cinematic Boot Overlay */}
      <AnimatePresence>
        {isBooting && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 bg-[#020617] flex flex-col items-center justify-center p-10"
          >
            <div className="relative mb-8">
              <div className="w-20 h-20 border-2 border-blue-500/10 border-t-blue-500 rounded-full animate-spin" />
              <Layers size={32} className="absolute inset-0 m-auto text-blue-500 animate-pulse" />
            </div>
            <div className="text-blue-500 font-mono text-[10px] tracking-[0.5em] uppercase font-black">Reconstructing Neural Map...</div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Logic Hub Header */}
      <div className="px-4 py-2 bg-white/5 border-b border-white/5 min-h-[60px] flex flex-col justify-center relative">
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-blue-500/30 to-transparent" />
        <div className="flex items-center justify-between mb-1.5">
           <div className="flex items-center gap-2.5">
              <div className="p-1 bg-blue-500/20 rounded-md border border-blue-500/30">
                 <Activity size={12} className="text-blue-400" />
              </div>
              <span className="text-[9px] font-black text-blue-500 uppercase tracking-[0.2em]">Synaptic Feedback</span>
           </div>
           <div className="flex items-center gap-3">
              <div className="text-[8px] text-slate-500 font-bold uppercase tracking-widest bg-slate-900 px-2.5 py-0.5 rounded-full border border-white/5">
                Sequence {currentStep} / {steps?.length || 0}
              </div>
           </div>
        </div>
        <p className="text-[11px] font-semibold text-slate-200 leading-snug italic opacity-90 pl-2 border-l-2 border-blue-500/30 line-clamp-2">
          {steps[currentStep - 1]?.description || 'Establish kernel link to initiate synaptic algorithm trace.'}
        </p>
      </div>
      
      {/* Visualization Canvas */}
      <div className="flex-1 relative bg-[radial-gradient(#1e293b_1.5px,transparent_1.5px)] [background-size:25px_25px]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          minZoom={0.2}
          maxZoom={1.5}
        />
      </div>
    </div>
  );
};

export default AlgorithmVisualizer;
