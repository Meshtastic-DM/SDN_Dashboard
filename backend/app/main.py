# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .state import (
  get_visible_entries,
  build_graph,
  reset_state,
)
from .feed_simulator import start_simulated_feed

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
