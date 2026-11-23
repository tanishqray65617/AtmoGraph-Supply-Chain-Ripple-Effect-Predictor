export interface SupplyNode {
  id: string;
  name: string;
  type: 'RawMaterialSupplier' | 'Manufacturer' | 'Port' | 'DistributionCenter' | 'Retailer';
  sector?: string;
  location: string;
  country: string;
  latitude: number;
  longitude: number;
  base_risk_score: number;
  current_risk_score: number;
  predicted_delay_days: number;
  criticality_tier?: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface SupplyEdge {
  id: string;
  source: string | SupplyNode;
  target: string | SupplyNode;
  type: string;
  lead_time_days: number;
  volume: number;
  reliability_score: number;
  criticality: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface NewsIncident {
  id: string;
  headline: string;
  content: string;
  target_entity: string;
  target_node_id?: string;
  disruption_type: string;
  severity_index: number;
  estimated_delay_days: number;
  timestamp: string;
}

export interface SimulationMetric {
  totalNodesAtRisk: number;
  averageDelayDays: number;
  maxPropagationHops: number;
  vulnerabilityIndex: number;
}

