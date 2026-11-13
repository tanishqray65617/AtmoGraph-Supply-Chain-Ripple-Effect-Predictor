import json
import os
import logging
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase, Driver
from app.core.config import settings

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.driver: Optional[Driver] = None
        self._memory_graph: Dict[str, Any] = {"nodes": [], "edges": []}
        self._load_local_fallback()

    def _load_local_fallback(self):
        """Load procedural supply chain graph as fallback memory store."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        unified_file = os.path.join(base_dir, "data", "supply_chain_data.json")
        if os.path.exists(unified_file):
            try:
                with open(unified_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._memory_graph = {
                        "nodes": data.get("nodes", []),
                        "edges": data.get("edges", [])
                    }
                    # Initialize risk fields
                    for n in self._memory_graph["nodes"]:
                        if "current_risk_score" not in n:
                            n["current_risk_score"] = n.get("base_risk_score", 0.0)
                        if "predicted_delay_days" not in n:
                            n["predicted_delay_days"] = 0.0
            except Exception as e:
                logger.warning(f"Could not load fallback supply_chain_data.json: {e}")

    def get_driver(self) -> Optional[Driver]:
        if self.driver is None:
            try:
                self.driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
            except Exception as e:
                logger.warning(f"Neo4j driver connection failed: {e}. Utilizing in-memory graph repository.")
                self.driver = None
        return self.driver

    def close(self):
        if self.driver:
            self.driver.close()

    def get_full_graph(self) -> Dict[str, Any]:
        driver = self.get_driver()
        if not driver:
            return self._memory_graph

        try:
            with driver.session(database=settings.NEO4J_DATABASE) as session:
                result = session.run("""
                    MATCH (n:SupplyNode)
                    OPTIONAL MATCH (n)-[r]->(m:SupplyNode)
                    RETURN collect(DISTINCT n) AS nodes, collect(DISTINCT {
                        id: toString(id(r)),
                        source: n.id,
                        target: m.id,
                        type: type(r),
                        lead_time_days: coalesce(r.lead_time_days, 7),
                        volume: coalesce(r.volume, 1000.0),
                        reliability_score: coalesce(r.reliability_score, 0.95),
                        criticality: coalesce(r.criticality, 'MEDIUM')
                    }) AS edges
                """)
                record = result.single()
                if record and record["nodes"]:
                    neo_nodes = [dict(n) for n in record["nodes"]]
                    neo_edges = [e for e in record["edges"] if e.get("target") is not None]
                    return {"nodes": neo_nodes, "edges": neo_edges}
        except Exception as e:
            logger.warning(f"Neo4j query failed, returning fallback graph: {e}")

        return self._memory_graph

    def update_node_risk(self, node_id: str, new_risk: float, delay_days: float = 0.0) -> bool:
        """Update node risk in both Neo4j and memory fallback."""
        updated = False
        # Update memory store
        for n in self._memory_graph["nodes"]:
            if n["id"] == node_id:
                n["current_risk_score"] = round(new_risk, 3)
                n["predicted_delay_days"] = round(delay_days, 1)
                updated = True
                break

        driver = self.get_driver()
        if driver:
            try:
                with driver.session(database=settings.NEO4J_DATABASE) as session:
                    session.run("""
                        MATCH (n:SupplyNode {id: $node_id})
                        SET n.risk_score = $risk,
                            n.predicted_delay_days = $delay,
                            n.updated_at = datetime()
                    """, node_id=node_id, risk=new_risk, delay=delay_days)
            except Exception as e:
                logger.error(f"Failed to update Neo4j node {node_id}: {e}")

        return updated

graph_service = GraphService()
