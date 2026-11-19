#!/usr/bin/env python3
"""
AtmoGraph Neo4j Graph Synchronization & Ingestion ETL
=====================================================
Author: Tanishq Ray <tanishqray65617@gmail.com>
Description: Connects to Neo4j database instance, applies constraints from
  schema/graph_schema.cypher, and syncs nodes and edges from data/supply_chain_data.json.
  Also provides bidirectional risk state sync between in-memory caches and persistent graph store.
"""

import json
import os
import sys
import logging
from typing import Dict, Any, List
from neo4j import GraphDatabase, Driver

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Neo4jSync")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "atmograph_secret_2026")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

class Neo4jGraphSync:
    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Driver = None

    def connect(self) -> bool:
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j instance at {self.uri}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j at {self.uri}: {e}")
            return False

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j driver connection.")

    def apply_schema(self, schema_file: str):
        if not os.path.exists(schema_file):
            logger.warning(f"Schema file not found at {schema_file}")
            return

        with open(schema_file, "r", encoding="utf-8") as f:
            cypher_content = f.read()

        statements = [stmt.strip() for stmt in cypher_content.split(";") if stmt.strip() and not stmt.strip().startswith("//")]

        with self.driver.session(database=NEO4J_DATABASE) as session:
            for stmt in statements:
                try:
                    session.run(stmt)
                    logger.info(f"Executed Cypher DDL: {stmt[:60]}...")
                except Exception as e:
                    logger.warning(f"DDL execution notice: {e}")

    def load_dataset(self, data_file: str):
        if not os.path.exists(data_file):
            logger.error(f"Dataset file {data_file} does not exist!")
            return

        with open(data_file, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        nodes = dataset.get("nodes", [])
        edges = dataset.get("edges", [])

        logger.info(f"Ingesting {len(nodes)} nodes into Neo4j...")
        with self.driver.session(database=NEO4J_DATABASE) as session:
            # Batch upsert nodes
            query_nodes = """
            UNWIND $batch AS n
            MERGE (node:SupplyNode {id: n.id})
            SET node.name = n.name,
                node.type = n.type,
                node.sector = n.sector,
                node.location = n.location,
                node.country = n.country,
                node.latitude = n.latitude,
                node.longitude = n.longitude,
                node.risk_score = coalesce(n.current_risk_score, n.base_risk_score, 0.0),
                node.predicted_delay_days = coalesce(n.predicted_delay_days, 0.0),
                node.criticality_tier = n.criticality_tier
            WITH node, n
            CALL apoc.create.addLabels(node, [n.type]) YIELD node AS labeledNode
            RETURN count(labeledNode)
            """
            try:
                session.run(query_nodes, batch=nodes)
                logger.info("Successfully ingested nodes batch with secondary labels.")
            except Exception as e:
                logger.info(f"APOC addLabels fallback to standard ingestion: {e}")
                fallback_query = """
                UNWIND $batch AS n
                MERGE (node:SupplyNode {id: n.id})
                SET node.name = n.name,
                    node.type = n.type,
                    node.sector = n.sector,
                    node.location = n.location,
                    node.country = n.country,
                    node.latitude = n.latitude,
                    node.longitude = n.longitude,
                    node.risk_score = coalesce(n.current_risk_score, n.base_risk_score, 0.0),
                    node.predicted_delay_days = coalesce(n.predicted_delay_days, 0.0),
                    node.criticality_tier = n.criticality_tier
                """
                session.run(fallback_query, batch=nodes)
                logger.info("Ingested nodes via fallback query.")

            # Batch upsert edges
            logger.info(f"Ingesting {len(edges)} relationships into Neo4j...")
            query_edges = """
            UNWIND $batch AS e
            MATCH (src:SupplyNode {id: e.source})
            MATCH (tgt:SupplyNode {id: e.target})
            MERGE (src)-[r:SUPPLIES_TO {id: e.id}]->(tgt)
            SET r.type = e.type,
                r.lead_time_days = e.lead_time_days,
                r.volume = e.volume,
                r.reliability_score = e.reliability_score,
                r.criticality = e.criticality
            """
            session.run(query_edges, batch=edges)
            logger.info("Successfully ingested graph edges into Neo4j.")

    def sync_risk_state(self, updates: List[Dict[str, Any]]):
        """Batch update risk properties across nodes."""
        query = """
        UNWIND $updates AS u
        MATCH (n:SupplyNode {id: u.id})
        SET n.risk_score = u.risk_score,
            n.predicted_delay_days = u.delay_days,
            n.updated_at = datetime()
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            session.run(query, updates=updates)
            logger.info(f"Synchronized {len(updates)} risk states to Neo4j.")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_path = os.path.join(base_dir, "schema", "graph_schema.cypher")
    data_path = os.path.join(base_dir, "data", "supply_chain_data.json")

    syncer = Neo4jGraphSync()
    if syncer.connect():
        syncer.apply_schema(schema_path)
        syncer.load_dataset(data_path)
        syncer.close()
    else:
        logger.warning("Neo4j database offline. In-memory engine will serve as operational primary.")

if __name__ == "__main__":
    main()
