# app/state.py
from typing import List, Dict, Any

VISIBLE_ENTRIES: List[Dict[str, Any]] = []


def append_entry(entry: Dict[str, Any]) -> None:
    VISIBLE_ENTRIES.append(entry)


def reset_state() -> None:
    global VISIBLE_ENTRIES
    VISIBLE_ENTRIES = []


def get_visible_entries() -> List[Dict[str, Any]]:
    return list(VISIBLE_ENTRIES)


def build_graph(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    node_map: Dict[int, Dict[str, Any]] = {}
    links: List[Dict[str, Any]] = []

    for r in entries:
        if not r.get("valid", True):
            continue

        self_id = int(r["selfId"])
        next_hop = int(r["nextHop"])
        dest_id = int(r["destId"])

        # nodes for self, nextHop, dest
        for nid in (self_id, next_hop, dest_id):
            if nid not in node_map:
                node_map[nid] = {
                    "id": nid,
                    "name": f"Node {nid}",
                }

        # link self → nextHop
        links.append({
            "source": self_id,
            "target": next_hop,
            "hopCount": int(r.get("hopCount", 1)),
            "destId": dest_id,
            "destSeqNum": int(r.get("destSeqNum", 0)),
        })

    # dedupe by (source, target, destId)
    seen = set()
    unique_links: List[Dict[str, Any]] = []
    for l in links:
        key = (l["source"], l["target"], l["destId"])
        if key in seen:
            continue
        seen.add(key)
        unique_links.append(l)

    return {
        "nodes": list(node_map.values()),
        "links": unique_links,
    }

