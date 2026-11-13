from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from app.services.graph_service import graph_service
from app.schemas.graph import GraphResponse, SupplyNodeModel, SupplyEdgeModel

router = APIRouter()

@router.get("/graph", response_model=GraphResponse)
async def get_supply_graph(
    sector: Optional[str] = Query(None, description="Filter nodes by industry sector"),
    min_risk: Optional[float] = Query(0.0, description="Minimum risk threshold")
):
    """Retrieve full supply chain topology graph with nodes, directed edges, and risk states."""
    graph_data = graph_service.get_full_graph()
    
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if sector:
        nodes = [n for n in nodes if n.get("sector") == sector]
        valid_node_ids = {n["id"] for n in nodes}
        edges = [e for e in edges if e["source"] in valid_node_ids and e["target"] in valid_node_ids]

    if min_risk > 0.0:
        nodes = [n for n in nodes if n.get("current_risk_score", 0.0) >= min_risk]
        valid_node_ids = {n["id"] for n in nodes}
        edges = [e for e in edges if e["source"] in valid_node_ids and e["target"] in valid_node_ids]

    return GraphResponse(
        nodes=nodes,
        edges=edges,
        total_nodes=len(nodes),
        total_edges=len(edges)
    )

@router.get("/graph/node/{node_id}", response_model=SupplyNodeModel)
async def get_node_by_id(node_id: str):
    """Fetch specific node attributes, risk metrics, and downstream telemetry."""
    graph_data = graph_service.get_full_graph()
    for n in graph_data.get("nodes", []):
        if n["id"] == node_id:
            return n
    raise HTTPException(status_code=404, detail=f"Node {node_id} not found in graph topology")

@router.post("/graph/reset")
async def reset_graph_risks():
    """Reset all node risk scores to baseline states."""
    graph_data = graph_service.get_full_graph()
    for n in graph_data.get("nodes", []):
        n["current_risk_score"] = n.get("base_risk_score", 0.0)
        n["predicted_delay_days"] = 0.0
    return {"status": "success", "message": "All node risks reset to baseline 0.0"}
