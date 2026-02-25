// src/pages/DashboardPage.jsx
import React, { useState} from "react";
import Layout from "../components/Layout.jsx";
import Header from "../components/Header.jsx";
import Sidebar from "../components/Sidebar.jsx";
import TopologyGraph from "../components/TopologyGraph.jsx";
import OfflineMapView from "../components/OfflineMapView.jsx";
import ExtendedNodeView from "../components/ExtendedNodeView.jsx";
import ControlsBar from "../components/ControlsBar.jsx";
import { useTopologyPolling } from "../hooks/useTopologyPolling.js";
// import { resetSimulation } from "../api/topologyApi.js";

const DashboardPage = () => {
  const [activeView, setActiveView] = useState('offline-map');
  const { graphData} = useTopologyPolling(5000);

  // const handleReset = useCallback(async () => {
  //   try {
  //     await resetSimulation();
  //   } catch (e) {
  //     console.error("Failed to reset simulation", e);
  //   }
  // }, []);

  const renderContent = () => {
    switch(activeView) {
      case 'offline-map':
        return <OfflineMapView graphData={graphData} />;
      case 'topology':
        return <TopologyGraph graphData={graphData} />;
      case 'extended-node':
        return <ExtendedNodeView />;
      case 'messaging':
        return <div className="view-placeholder">Messaging - Coming Soon</div>;
      case 'route-analysis':
        return <div className="view-placeholder">Route Analysis - Coming Soon</div>;
      default:
        return <TopologyGraph graphData={graphData} />;
    }
  };

  return (
    <Layout>
      <Header />
      <div className="layout-container">
        <Sidebar activeView={activeView} onViewChange={setActiveView} />
        <div className="main-content">
          {renderContent()}
        </div>
      </div>
    </Layout>
  );
};

export default DashboardPage;
