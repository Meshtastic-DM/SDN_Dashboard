# app/feed_simulator.py
import asyncio
from .state import append_entry

# Simulated time-series of routing entries (your sample data)
ALL_ENTRIES = [
  {
    "selfId": 1,
    "destId": 2,
    "nextHop": 2,
    "hopCount": 1,
    "destSeqNum": 5,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 1,
    "destId": 0,
    "nextHop": 0,
    "hopCount": 1,
    "destSeqNum": 3,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 2,
    "destId": 1,
    "nextHop": 1,
    "hopCount": 1,
    "destSeqNum": 2,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 2,
    "destId": 0,
    "nextHop": 0,
    "hopCount": 1,
    "destSeqNum": 6,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 2,
    "destId": 4,
    "nextHop": 5,
    "hopCount": 2,
    "destSeqNum": 34,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 2,
    "destId": 5,
    "nextHop": 3,
    "hopCount": 2,
    "destSeqNum": 12,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 2,
    "destId": 3,
    "nextHop": 3,
    "hopCount": 1,
    "destSeqNum": 27,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 1,
    "destId": 3,
    "nextHop": 2,
    "hopCount": 2,
    "destSeqNum": 27,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 2,
    "destId": 5,
    "nextHop": 5,
    "hopCount": 1,
    "destSeqNum": 57,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 1,
    "destId": 5,
    "nextHop": 2,
    "hopCount": 2,
    "destSeqNum": 57,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 3,
    "destId": 2,
    "nextHop": 2,
    "hopCount": 1,
    "destSeqNum": 5,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 3,
    "destId": 4,
    "nextHop": 4,
    "hopCount": 1,
    "destSeqNum": 23,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 3,
    "destId": 1,
    "nextHop": 2,
    "hopCount": 2,
    "destSeqNum": 14,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 5,
    "destId": 2,
    "nextHop": 2,
    "hopCount": 1,
    "destSeqNum": 5,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 3,
    "destId": 0,
    "nextHop": 2,
    "hopCount": 2,
    "destSeqNum": 61,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  },
  {
    "selfId": 5,
    "destId": 4,
    "nextHop": 4,
    "hopCount": 1,
    "destSeqNum": 23,
    "valid": True,
    "precursorList": [],
    "lifeTime": 300000
  }
]

FEED_INTERVAL_SECONDS = 1.5  # one entry every 1.5 s


async def feeder_loop():
  """Simulate SDN node sending routing entries over time."""
  for entry in ALL_ENTRIES:
    append_entry(entry)
    await asyncio.sleep(FEED_INTERVAL_SECONDS)


async def start_simulated_feed():
  """Start the simulated feeder as a background task."""
  asyncio.create_task(feeder_loop())
