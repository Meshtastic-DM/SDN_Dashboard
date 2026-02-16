# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from .state import (
  get_visible_entries,
  build_graph,
  reset_state,
)
from .feed_simulator import start_simulated_feed
from .meshtastic_service import fetch_all_nodes, format_node_for_display

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173", "http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
  # start simulated SDN feed
  reset_state()
  await start_simulated_feed()


@app.get("/api/topology")
def get_topology():
  """Current topology based on entries received so far."""
  entries = get_visible_entries()
  return build_graph(entries)


@app.get("/api/entries")
def api_get_entries():
  """Raw routing entries (for debugging)."""
  entries = get_visible_entries()
  return {
    "count": len(entries),
    "entries": entries,
  }


@app.post("/api/reset")
async def reset_simulation():
  """Reset and restart simulator."""
  reset_state()
  await start_simulated_feed()
  return {"status": "reset"}


@app.get("/api/meshtastic/nodes")
def get_meshtastic_nodes(ports: Optional[str] = None):
  """
  Fetch Meshtastic node information from specified ports.
  
  Args:
      ports: Comma-separated list of ports (e.g., "4403,4404,4405")
            If not provided, defaults to [4403, 4404, 4405, 4406, 4407]
  
  Returns:
      List of formatted node data from each port
  """
  if ports:
    port_list = [int(p.strip()) for p in ports.split(",")]
  else:
    port_list = [4403, 4404, 4405, 4406, 4407]
  
  nodes_data = fetch_all_nodes(port_list)
  formatted_nodes = [format_node_for_display(node) for node in nodes_data]
  
  return {
    "count": len(formatted_nodes),
    "nodes": formatted_nodes
  }


@app.get("/api/meshtastic/node/{port}")
def get_meshtastic_node(port: int):
  """
  Fetch Meshtastic node information from a specific port.
  
  Args:
      port: TCP port number
  
  Returns:
      Formatted node data
  """
  from .meshtastic_service import fetch_meshtastic_info
  
  node_data = fetch_meshtastic_info(port=port)
  if node_data:
    node_data["port"] = port
    return format_node_for_display(node_data)
  
  return {"error": f"Failed to fetch data from port {port}"}
