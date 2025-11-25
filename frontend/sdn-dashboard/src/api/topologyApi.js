// src/api/topologyApi.js
const API_BASE = "http://localhost:8000"; // Python FastAPI backend

export async function fetchTopology() {
  const res = await fetch(`${API_BASE}/api/topology`);
  if (!res.ok) throw new Error("Failed to fetch topology");
  return res.json();
}

export async function fetchEntries() {
  const res = await fetch(`${API_BASE}/api/entries`);
  if (!res.ok) throw new Error("Failed to fetch entries");
  return res.json();
}

export async function resetSimulation() {
  const res = await fetch(`${API_BASE}/api/reset`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to reset simulation");
  return res.json();
}
