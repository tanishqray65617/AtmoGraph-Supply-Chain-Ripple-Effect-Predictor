import json
import asyncio
import logging
from typing import List, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.graph_service import graph_service
from ml.gnn_model import ripple_predictor

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        payload = json.dumps(message)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead_connections.append(connection)
        for dc in dead_connections:
            self.active_connections.discard(dc)

manager = ConnectionManager()

@router.websocket("/ws/risk-stream")
async def risk_stream_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket endpoint that streams graph telemetry,
    live GNN inference results, and ripple shock notifications.
    """
    await manager.connect(websocket)
    try:
        # Initial handshake: send current graph state
        graph_data = graph_service.get_full_graph()
        await websocket.send_text(json.dumps({
            "type": "INITIAL_GRAPH_STATE",
            "data": graph_data
        }))

        while True:
            # Receive client trigger / shock simulation commands
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")

            if action == "TRIGGER_SHOCK":
                node_id = message.get("node_id")
                shock_val = float(message.get("severity", 0.85))
                delay_val = float(message.get("delay_days", 14.0))

                # Update primary shocked node
                graph_service.update_node_risk(node_id, shock_val, delay_val)

                # Compute GNN downstream ripple effect
                current_graph = graph_service.get_full_graph()
                ripple_results = ripple_predictor.predict_ripple(
                    current_graph.get("nodes", []),
                    current_graph.get("edges", [])
                )

                # Apply propagated risks across downstream nodes
                for nid, metrics in ripple_results.items():
                    graph_service.update_node_risk(
                        nid,
                        metrics["risk_score"],
                        metrics["predicted_delay"]
                    )

                # Broadcast updated graph state to all connected clients
                updated_graph = graph_service.get_full_graph()
                await manager.broadcast({
                    "type": "GRAPH_RISK_UPDATED",
                    "origin_node_id": node_id,
                    "ripple_predictions": ripple_results,
                    "updated_graph": updated_graph
                })

            elif action == "PING":
                await websocket.send_text(json.dumps({"type": "PONG"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
