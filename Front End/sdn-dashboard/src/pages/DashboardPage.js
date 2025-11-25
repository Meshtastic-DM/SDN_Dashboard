// src/pages/DashboardPage.js
import React, { useCallback } from "react";
import Layout from "../components/Layout";
import TopologyGraph from "../components/TopologyGraph";
import ControlsBar from "../components/ControlsBar";
import { useTopologyPolling } from "../hooks/useTopologyPolling";
import { resetSimulation } from "../api/topologyApi";

const DashboardPage = () => {
  const { graphData, entryCount, loading, error } = useTopologyPolling(1000);

  const handleReset = useCallback(async () => {
    try {
      await resetSimulation();
    } catch (e) {
      console.error("Failed to reset simulation", e);
    }
  }, []);

  return (
    <Layout>
      <h1 style={{ marginBottom: 4 }}>Meshtastic SDN Dashboard</h1>
      <p style={{ marginBottom: 16, fontSize: 14, color: "#9ca3af" }}>
        Topology built from routing entries received by the SDN controller
        backend.
      </p>

      <ControlsBar
        entryCount={entryCount}
        onReset={handleReset}
        loading={loading}
        error={error}
      />

      <TopologyGraph graphData={graphData} />
    </Layout>
  );
};

export default DashboardPage;
