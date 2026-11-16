import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { SupplyNode, SupplyEdge } from '../types/graph';

interface NetworkGraphProps {
  nodes: SupplyNode[];
  edges: SupplyEdge[];
  selectedNode: SupplyNode | null;
  onSelectNode: (node: SupplyNode | null) => void;
  riskThreshold: number;
}

const TYPE_COLORS: Record<string, string> = {
  RawMaterialSupplier: '#3b82f6', // blue
  Manufacturer: '#8b5cf6',       // purple
  Port: '#06b6d4',               // cyan
  DistributionCenter: '#f59e0b', // amber
  Retailer: '#10b981'            // emerald
};

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  nodes,
  edges,
  selectedNode,
  onSelectNode,
  riskThreshold
}) => {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const zoomTransformRef = useRef<d3.ZoomTransform>(d3.zoomIdentity);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const width = svgRef.current.clientWidth || 800;
    const height = svgRef.current.clientHeight || 600;

    svg.selectAll('*').remove();

    // Defs for glow filter & arrowheads
    const defs = svg.append('defs');

    // Arrow markers
    defs.append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 22)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#4b5563');

    defs.append('marker')
      .attr('id', 'arrow-risk')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 22)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#ef4444');

    // Glow filter for high risk nodes
    const filter = defs.append('filter').attr('id', 'glow');
    filter.append('feGaussianBlur').attr('stdDeviation', '4').attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    const container = svg.append('g').attr('class', 'graph-container');

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on('zoom', (event) => {
        zoomTransformRef.current = event.transform;
        container.attr('transform', event.transform);
      });

    svg.call(zoom).call(zoom.transform, zoomTransformRef.current);

    // Deep copy graph data for D3 force simulation
    const simulationNodes = nodes.map(d => ({ ...d }));
    const nodeMap = new Map(simulationNodes.map(d => [d.id, d]));
    
    const simulationLinks = edges
      .filter(e => {
        const src = typeof e.source === 'object' ? e.source.id : e.source;
        const tgt = typeof e.target === 'object' ? e.target.id : e.target;
        return nodeMap.has(src) && nodeMap.has(tgt);
      })
      .map(e => ({
        ...e,
        source: nodeMap.get(typeof e.source === 'object' ? e.source.id : e.source)!,
        target: nodeMap.get(typeof e.target === 'object' ? e.target.id : e.target)!
      }));

    // Setup Force Simulation
    const simulation = d3.forceSimulation<any>(simulationNodes)
      .force('link', d3.forceLink<any, any>(simulationLinks).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(28));

    // Render Edges
    const link = container.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(simulationLinks)
      .enter()
      .append('line')
      .attr('stroke', (d) => {
        const srcRisk = d.source.current_risk_score || 0;
        const tgtRisk = d.target.current_risk_score || 0;
        return (srcRisk > riskThreshold || tgtRisk > riskThreshold) ? '#ef4444' : '#374151';
      })
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => (d.criticality === 'CRITICAL' ? 2.5 : 1.5))
      .attr('marker-end', (d) => {
        const srcRisk = d.source.current_risk_score || 0;
        const tgtRisk = d.target.current_risk_score || 0;
        return (srcRisk > riskThreshold || tgtRisk > riskThreshold) ? 'url(#arrow-risk)' : 'url(#arrow)';
      });

    // Render Node Groups
    const node = container.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(simulationNodes)
      .enter()
      .append('g')
      .attr('cursor', 'pointer')
      .on('click', (_, d) => {
        onSelectNode(d);
      })
      .call(
        d3.drag<any, any>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    // Node Outer Ring / Ripple Pulse for High Risk
    node.each(function(d) {
      const g = d3.select(this);
      const isHighRisk = (d.current_risk_score || 0) >= 0.7;
      if (isHighRisk) {
        g.append('circle')
          .attr('r', 20)
          .attr('fill', 'none')
          .attr('stroke', '#ef4444')
          .attr('stroke-width', 2)
          .attr('stroke-opacity', 0.8)
          .attr('class', 'animate-ping');
      }
    });

    // Node Circle
    node.append('circle')
      .attr('r', d => (selectedNode?.id === d.id ? 16 : 12))
      .attr('fill', (d) => {
        const risk = d.current_risk_score || 0;
        if (risk >= 0.75) return '#ef4444'; // Red
        if (risk >= 0.40) return '#f59e0b'; // Amber
        return TYPE_COLORS[d.type] || '#6b7280';
      })
      .attr('stroke', (d) => (selectedNode?.id === d.id ? '#ffffff' : '#1f2937'))
      .attr('stroke-width', d => (selectedNode?.id === d.id ? 3 : 1.5))
      .attr('filter', (d) => ((d.current_risk_score || 0) >= 0.6 ? 'url(#glow)' : null));

    // Node Label
    node.append('text')
      .text(d => d.name)
      .attr('x', 16)
      .attr('y', 4)
      .attr('font-size', '10px')
      .attr('fill', '#e5e7eb')
      .attr('font-weight', '500')
      .attr('pointer-events', 'none')
      .attr('opacity', 0.85);

    // Simulation Tick Updates
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [nodes, edges, selectedNode, riskThreshold]);

  return (
    <div className="w-full h-full relative overflow-hidden bg-[#070b12]">
      <svg ref={svgRef} className="w-full h-full select-none" />
    </div>
  );
};
