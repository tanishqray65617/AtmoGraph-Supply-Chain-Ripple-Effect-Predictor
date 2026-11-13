from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.schemas.graph import NewsIngestRequest, NewsIngestResponse
from app.services.graph_service import graph_service

router = APIRouter()

@router.post("/ingest", response_model=NewsIngestResponse)
async def ingest_news_feed(payload: NewsIngestRequest):
    """
    Ingest unstructured news alerts or incident reports.
    Extract affected supply chain entities, evaluate shock severity,
    and update graph risk states.
    """
    text = f"{payload.headline}. {payload.content}"
    graph_data = graph_service.get_full_graph()
    nodes = graph_data.get("nodes", [])

    matched_nodes = []
    # Match node names or locations against the news content
    for node in nodes:
        name = node.get("name", "")
        location = node.get("location", "")
        if (name and name.lower() in text.lower()) or (location and location.lower() in text.lower()):
            matched_nodes.append({
                "id": node["id"],
                "name": name,
                "type": node["type"],
                "location": location
            })

    severity = payload.override_severity or 0.85 if matched_nodes else 0.10
    disruption = len(matched_nodes) > 0

    # Apply initial shock to matched nodes
    for mn in matched_nodes:
        graph_service.update_node_risk(mn["id"], severity, delay_days=severity * 20.0)

    return NewsIngestResponse(
        status="processed",
        extracted_entities=[{"text": mn["name"], "label": "SUPPLY_ENTITY"} for mn in matched_nodes],
        matched_nodes=matched_nodes,
        disruption_detected=disruption,
        assessed_risk_score=severity,
        propagation_summary={
            "initial_shock_nodes": len(matched_nodes),
            "estimated_tier1_delay_days": round(severity * 15.0, 1)
        }
    )
