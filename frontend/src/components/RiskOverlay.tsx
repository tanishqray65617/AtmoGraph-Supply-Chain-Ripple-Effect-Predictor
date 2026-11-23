import React from 'react';
import { SupplyNode } from '../types/graph';
import { AlertTriangle, Clock, Layers } from 'lucide-react';

interface RiskOverlayProps {
  nodes: SupplyNode[];
  selectedNode?: SupplyNode | null;
  onSimulateShock?: (nodeId: string) => void;
}

export const RiskOverlay: React.FC<RiskOverlayProps> = ({
  nodes
}) => {
  const atRiskNodes = nodes.filter(n => (n.current_risk_score || 0) > 0.35);
  const totalDelayHours = atRiskNodes.reduce((acc, curr) => acc + (curr.predicted_delay_days || 0) * 24, 0);

  return (
    <div className="absolute bottom-5 left-5 z-20 flex gap-4 pointer-events-none">
      {/* Metric Cards Bar */}
      <div className="pointer-events-auto bg-gray-950/85 backdrop-blur-md border border-gray-800 rounded-xl p-3.5 shadow-2xl flex items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-red-400" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold tracking-wider text-gray-400">
              Vulnerable Nodes
            </div>
            <div className="text-lg font-bold font-mono text-white flex items-baseline gap-1.5">
              {atRiskNodes.length}
              <span className="text-[11px] font-normal text-gray-400">/ {nodes.length}</span>
            </div>
          </div>
        </div>

        <div className="w-px h-8 bg-gray-800" />

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
            <Clock className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold tracking-wider text-gray-400">
              Est. Backlog Delay
            </div>
            <div className="text-lg font-bold font-mono text-amber-400">
              {Math.round(totalDelayHours)} hrs
            </div>
          </div>
        </div>

        <div className="w-px h-8 bg-gray-800" />

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
            <Layers className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold tracking-wider text-gray-400">
              Cascading Hops
            </div>
            <div className="text-lg font-bold font-mono text-purple-300">
              3 Hops Deep
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

