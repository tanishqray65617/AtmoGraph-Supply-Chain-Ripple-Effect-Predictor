import React, { useState } from 'react';
import { Activity, ShieldAlert, Cpu, Globe, Sliders } from 'lucide-react';
import { SupplyNode, NewsIncident } from './types/graph';

export const App: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<SupplyNode | null>(null);
  const [riskThreshold, setRiskThreshold] = useState<number>(0.2);

  return (
    <div className="flex flex-col h-screen w-screen bg-[#0b0f19] text-slate-100 overflow-hidden font-sans">
      {/* Top Navigation Bar */}
      <header className="h-14 border-b border-gray-800 bg-gray-950/80 backdrop-blur px-6 flex items-center justify-between z-20">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-wide text-white flex items-center gap-2">
              AtmoGraph
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-900/60 text-blue-400 border border-blue-700/50">
                GNN v1.0
              </span>
            </h1>
            <p className="text-[10px] text-gray-400">Supply Chain Ripple Effect Predictor</p>
          </div>
        </div>

        <div className="flex items-center space-x-6 text-xs text-gray-300">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Graph Live: 50 Nodes</span>
          </div>
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            <span>GNN Inference: Active</span>
          </div>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar: Disruption Feed & Incident Controls */}
        <aside className="w-80 border-r border-gray-800 bg-gray-900/60 flex flex-col z-10 custom-scrollbar overflow-y-auto p-4 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-gray-800">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Live News Disruption Feeds
            </h2>
          </div>
          <p className="text-xs text-gray-400">
            Select incidents to simulate localized upstream shocks and visualize cascading ripple propagation.
          </p>

          <div className="space-y-3">
            <div className="p-3 rounded-lg bg-gray-800/60 border border-gray-700 hover:border-blue-500 cursor-pointer transition">
              <div className="flex justify-between items-start text-xs font-semibold text-gray-200">
                <span>Port of Rotterdam Strike</span>
                <span className="text-red-400 font-mono">Sev 0.85</span>
              </div>
              <p className="text-[11px] text-gray-400 mt-1">
                Dockworker dispute halts container throughput across terminals.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-gray-800/60 border border-gray-700 hover:border-blue-500 cursor-pointer transition">
              <div className="flex justify-between items-start text-xs font-semibold text-gray-200">
                <span>Shanghai Typhoon In-fa</span>
                <span className="text-red-400 font-mono">Sev 0.92</span>
              </div>
              <p className="text-[11px] text-gray-400 mt-1">
                Category 4 winds halt vessel berthing and outbound components.
              </p>
            </div>
          </div>
        </aside>

        {/* Center: Interactive Graph Viewport Canvas */}
        <main className="flex-1 relative flex flex-col bg-[#080c14] overflow-hidden">
          <div className="absolute top-4 left-4 z-10 flex gap-2">
            <div className="px-3 py-1.5 rounded-md bg-gray-900/90 border border-gray-700 text-xs flex items-center gap-2 shadow-lg">
              <Sliders className="w-3.5 h-3.5 text-blue-400" />
              <label>Risk Threshold: {riskThreshold.toFixed(2)}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={riskThreshold}
                onChange={(e) => setRiskThreshold(parseFloat(e.target.value))}
                className="w-24 accent-blue-500"
              />
            </div>
          </div>

          <div id="graph-viewport-placeholder" className="w-full h-full flex items-center justify-center text-gray-500 text-sm">
            <div className="text-center space-y-2">
              <Globe className="w-12 h-12 text-gray-600 mx-auto animate-spin-slow" />
              <p>Topological Supply Chain Graph Rendering Engine Initializing...</p>
            </div>
          </div>
        </main>

        {/* Right Flyout Inspector */}
        <aside className="w-80 border-l border-gray-800 bg-gray-900/60 p-4 flex flex-col z-10 custom-scrollbar overflow-y-auto">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 pb-2 border-b border-gray-800">
            Node Telemetry & Impact
          </h2>
          {selectedNode ? (
            <div className="mt-4 space-y-3 text-xs">
              <div>
                <span className="text-gray-500">Node Identifier:</span>
                <p className="font-mono text-blue-400">{selectedNode.id}</p>
              </div>
              <div>
                <span className="text-gray-500">Entity Name:</span>
                <p className="font-semibold text-gray-200">{selectedNode.name}</p>
              </div>
              <div>
                <span className="text-gray-500">Node Type:</span>
                <p className="text-gray-300">{selectedNode.type}</p>
              </div>
              <div>
                <span className="text-gray-500">Location:</span>
                <p className="text-gray-300">{selectedNode.location}, {selectedNode.country}</p>
              </div>
            </div>
          ) : (
            <div className="mt-8 text-center text-xs text-gray-500">
              Click any node in the graph viewport to inspect attributes, upstream dependencies, and delay propagation forecasts.
            </div>
          )}
        </aside>
      </div>
    </div>
  );
};

export default App;
