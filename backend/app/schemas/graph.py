from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SupplyNodeModel(BaseModel):
    id: str
    name: str
    type: str
    sector: Optional[str] = "General"
    location: str
    country: str
    latitude: float
    longitude: float
    base_risk_score: float = 0.0
    current_risk_score: float = 0.0
    predicted_delay_days: float = 0.0
    criticality_tier: Optional[int] = 2
    attributes: Dict[str, Any] = Field(default_factory=dict)

class SupplyEdgeModel(BaseModel):
    id: str
    source: str
    target: str
    type: str
    lead_time_days: int
    volume: float
    reliability_score: float = 0.95
    criticality: str = "MEDIUM"

class GraphResponse(BaseModel):
    nodes: List[SupplyNodeModel]
    edges: List[SupplyEdgeModel]
    total_nodes: int
    total_edges: int

class NewsIngestRequest(BaseModel):
    headline: str
    content: str
    source_url: Optional[str] = None
    override_severity: Optional[float] = None

class NewsIngestResponse(BaseModel):
    status: str
    extracted_entities: List[Dict[str, Any]]
    matched_nodes: List[Dict[str, Any]]
    disruption_detected: bool
    assessed_risk_score: float
    propagation_summary: Dict[str, Any]
