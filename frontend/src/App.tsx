import React, { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Cpu, Globe, Sliders, RefreshCw, ZoomIn, ZoomOut, Play } from 'lucide-react';
import { SupplyNode, SupplyEdge, NewsIncident } from './types/graph';
import { NetworkGraph } from './components/NetworkGraph';

export const App: React.FC = () => {
  const [nodes, setNodes] = useState<SupplyNode[]>([]);
  const [edges, setEdges] = useState<SupplyEdge[]>([]);
  const [news, setNews] = useState<NewsIncident[]>([]);
  const [selectedNode, setSelectedNode] = useState<SupplyNode | null>(null);
  const [riskThreshold, setRiskThreshold] = useState<number>(0.3);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeSimulation, setActiveSimulation] = useState<string | null>(null);

  // Fetch initial graph topology and news incidents
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/v1/graph');
        if (res.ok) {
          const data = await res.json();
          setNodes(data.nodes || []);
          setEdges(data.edges || []);
        } else {
          // Fallback to static mock if backend is not yet started
          const fallbackData = await import('../../data/supply_chain_data.json');
          setNodes(fallbackData.nodes as SupplyNode[]);
          setEdges(fallbackData.edges as SupplyEdge[]);
          setNews(fallbackData.news as NewsIncident[]);
        }
      } catch (err) {
        console.warn('API fetch failed, falling back to local dataset', err);
        try {
          const fallbackData = await import('../../data/supply_chain_data.json');
          setNodes(fallbackData.nodes as SupplyNode[]);
          setEdges(fallbackData.edges as SupplyEdge[]);
          setNews(fallbackData.news as NewsIncident[]);
        } catch (e) {
          console.error('Failed to load local data fallback:', e);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSimulateDisruption = async (incident: NewsIncident) => {
    setActiveSimulation(incident.headline);
    try {
      const res = await fetch('/api/v1/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          headline: incident.headline,
          content: incident.content,
          override_severity: incident.severity_index
        })
      });

      if (res.ok) {
        // Refetch updated graph with newly updated risks
        const graphRes = await fetch('/api/v1/graph');
        if (graphRes.ok) {
          const updated = await graphRes.json();
          setNodes(updated.nodes);
          setEdges(updated.edges);
        }
      } else {
        // Fallback local ripple simulation
        setNodes(prev => prev.map(n => {
          if (n.name.toLowerCase().includes(incident.target_entity.toLowerCase())) {
            return {
              ...n,
              current_risk_score: incident.severity_index,
              predicted_delay_days: incident.estimated_delay_days
            };
          }
          return n;
        }));
      }
    } catch (err) {
      // Local fallback
      setNodes(prev => prev.map(n => {
        if (n.name.toLowerCase().includes(incident.target_entity.toLowerCase())) {
          return {
            ...n,
            current_risk_score: incident.severity_index,
            predicted_delay_days: incident.estimated_delay_days
          };
        }
        return n;
      }));
    }
  };

  const handleReset = async () => {
    try {
      await fetch('/api/v1/graph/reset', { method: 'POST' });
    } catch (e) {
      // ignore
    }
    setNodes(prev => prev.map(n => ({ ...n, current_risk_score: n.base_risk_score, predicted_delay_days: 0 })));
    setSelectedNode(null);
    setActiveSimulation(null);
  };

  const highRiskCount = nodes.filter(n => (n.current_risk_score || 0) >= 0.5).length;

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
            <span className={`w-2 h-2 rounded-full ${highRiskCount > 0 ? 'bg-red-500 animate-ping' : 'bg-emerald-500'}`} />
            <span>High Risk Nodes: {highRiskCount}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Globe className="w-4 h-4 text-blue-400" />
            <span>Active Nodes: {nodes.length}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            <span>PyG GNN: Ready</span>
          </div>
          <button
            onClick={handleReset}
            className="px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 flex items-center gap-1.5 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset State
          </button>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar: Disruption Feed */}
        <aside className="w-84 border-r border-gray-800 bg-gray-900/60 flex flex-col z-10 custom-scrollbar overflow-y-auto p-4 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-gray-800">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              Live News Disruption Feeds
            </h2>
          </div>
          <p className="text-[11px] text-gray-400 leading-relaxed">
            Trigger global incident alerts to inject shocks into the topological network and observe downstream propagation.
          </p>

          <div className="space-y-3">
            {news.map(incident => (
              <div
                key={incident.id}
                onClick={() => handleSimulateDisruption(incident)}
                className={`p-3 rounded-lg border cursor-pointer transition ${
                  activeSimulation === incident.headline
                    ? 'bg-blue-950/40 border-blue-500 ring-1 ring-blue-500'
                    : 'bg-gray-800/60 border-gray-700 hover:border-gray-500'
                }`}
              >
                <div className="flex justify-between items-start text-xs font-semibold text-gray-200">
                  <span className="line-clamp-1">{incident.headline}</span>
                </div>
                <p className="text-[11px] text-gray-400 mt-1 line-clamp-2">{incident.content}</p>
                <div className="mt-2.5 flex items-center justify-between text-[10px] text-gray-400 border-t border-gray-800 pt-2">
                  <span className="font-mono text-red-400">Severity: {(incident.severity_index * 100).toFixed(0)}%</span>
                  <span className="text-blue-400 flex items-center gap-1">
                    <Play className="w-3 h-3 fill-current" /> Inject Shock
                  </span>
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* Center: D3.js Network Graph Viewport */}
        <main className="flex-1 relative flex flex-col bg-[#070b12] overflow-hidden">
          {/* Top Controls Overlay */}
          <div className="absolute top-4 left-4 z-10 flex gap-3">
            <div className="px-3.5 py-2 rounded-lg bg-gray-900/90 backdrop-blur border border-gray-800 text-xs flex items-center gap-3 shadow-xl">
              <Sliders className="w-3.5 h-3.5 text-blue-400" />
              <label className="text-gray-300">Highlight Edge Threshold: {riskThreshold.toFixed(2)}</label>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={riskThreshold}
                onChange={(e) => setRiskThreshold(parseFloat(e.target.value))}
                className="w-24 accent-blue-500 cursor-pointer"
              />
            </div>

            {/* Legend */}
            <div className="px-3.5 py-2 rounded-lg bg-gray-900/90 backdrop-blur border border-gray-800 text-[11px] flex items-center gap-4 shadow-xl text-gray-300">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500" /> Supplier</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-cyan-500" /> Port</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-purple-500" /> Manufacturer</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> DC</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Retailer</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" /> Disrupted</span>
            </div>
          </div>

          {isLoading ? (
            <div className="w-full h-full flex items-center justify-center text-gray-500 text-sm">
              <div className="text-center space-y-2">
                <Globe className="w-12 h-12 text-blue-500 mx-auto animate-spin" />
                <p>Synthesizing Supply Chain Topology...</p>
              </div>
            </div>
          ) : (
            <NetworkGraph
              nodes={nodes}
              edges={edges}
              selectedNode={selectedNode}
              onSelectNode={setSelectedNode}
              riskThreshold={riskThreshold}
            />
          )}
        </main>

        {/* Right Flyout Inspector */}
        <aside className="w-80 border-l border-gray-800 bg-gray-900/60 p-4 flex flex-col z-10 custom-scrollbar overflow-y-auto">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 pb-2 border-b border-gray-800">
            Node Telemetry & Impact
          </h2>
          {selectedNode ? (
            <div className="mt-4 space-y-4 text-xs">
              <div className="p-3 rounded-lg bg-gray-800/80 border border-gray-700">
                <span className="text-[10px] text-gray-400 uppercase tracking-wider">Node ID</span>
                <p className="font-mono text-sm font-bold text-blue-400 mt-0.5">{selectedNode.id}</p>
                <h3 className="text-sm font-semibold text-white mt-2">{selectedNode.name}</h3>
                <span className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] bg-gray-700 text-gray-300">
                  {selectedNode.type}
                </span>
              </div>

              <div className="space-y-2.5">
                <div className="flex justify-between py-1 border-b border-gray-800 text-gray-300">
                  <span className="text-gray-500">Location:</span>
                  <span>{selectedNode.location}, {selectedNode.country}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-800 text-gray-300">
                  <span className="text-gray-500">Current Shock Index:</span>
                  <span className={`font-mono font-bold ${(selectedNode.current_risk_score || 0) >= 0.5 ? 'text-red-400' : 'text-emerald-400'}`}>
                    {((selectedNode.current_risk_score || 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-800 text-gray-300">
                  <span className="text-gray-500">Predicted Delay:</span>
                  <span className="font-mono font-bold text-amber-400">
                    +{selectedNode.predicted_delay_days || 0} days
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-800 text-gray-300">
                  <span className="text-gray-500">Criticality Tier:</span>
                  <span className="text-gray-200">Tier {selectedNode.criticality_tier || 2}</span>
                </div>
              </div>

              {/* Action Trigger */}
              <div className="pt-2">
                <button
                  onClick={() => {
                    setNodes(prev => prev.map(n => n.id === selectedNode.id ? { ...n, current_risk_score: 0.9, predicted_delay_days: 22 } : n));
                    setSelectedNode(prev => prev ? { ...prev, current_risk_score: 0.9, predicted_delay_days: 22 } : null);
                  }}
                  className="w-full py-2 px-3 rounded-lg bg-red-600/20 border border-red-500/40 text-red-300 hover:bg-red-600/30 font-medium text-xs transition"
                >
                  Manually Disrupt Node
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-12 text-center text-xs text-gray-500 space-y-2">
              <Globe className="w-8 h-8 text-gray-600 mx-auto" />
              <p>Click any node in the topology network to inspect attributes, upstream logistics, and delay propagation forecasts.</p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
};

export default App;
