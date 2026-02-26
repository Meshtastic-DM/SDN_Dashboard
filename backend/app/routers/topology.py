from fastapi import APIRouter
from ..startup_functions.state import get_visible_entries, build_graph, reset_state
from ..startup_functions.feed_simulator import start_simulated_feed

router = APIRouter(prefix="/api", tags=["topology"])

@router.get("/topology")
def get_topology():
    entries = get_visible_entries()
    return build_graph(entries)

@router.get("/entries")
def api_get_entries():
    entries = get_visible_entries()
    return {"count": len(entries), "entries": entries}

@router.post("/reset")
async def reset_simulation():
    reset_state()
    await start_simulated_feed()
    return {"status": "reset"}