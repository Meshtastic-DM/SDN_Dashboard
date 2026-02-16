// src/components/ExtendedNodeView.jsx
import React, { useState, useEffect } from 'react';
import './ExtendedNodeView.css';

const ExtendedNodeView = () => {
  const [nodesData, setNodesData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSections, setExpandedSections] = useState({});

  const fetchNodes = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/meshtastic/nodes');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setNodesData(data.nodes || []);
    } catch (err) {
      setError(`Failed to fetch node data: ${err.message}`);
      console.error('Error fetching Meshtastic nodes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // fetchNodes();
    // Auto-refresh every 30 seconds
    // const interval = setInterval(fetchNodes, 30000);
    // return () => clearInterval(interval);
  }, []);

  const toggleSection = (nodePort, section) => {
    const key = `${nodePort}-${section}`;
    setExpandedSections(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const isSectionExpanded = (nodePort, section) => {
    const key = `${nodePort}-${section}`;
    return expandedSections[key] || false;
  };

  const formatBattery = (level) => {
    if (level === 101) return 'Powered';
    if (level === null || level === undefined) return 'N/A';
    return `${level}%`;
  };

  const getBatteryClass = (level) => {
    if (level === 101 || level >= 75) return 'good';
    if (level >= 30) return 'medium';
    return 'poor';
  };

  const getSnrClass = (snr) => {
    if (snr >= -5) return 'good';
    if (snr >= -12) return 'medium';
    return 'poor';
  };

  const formatUptime = (seconds) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const renderCollapsibleSection = (title, content, nodePort, sectionKey) => {
    const isOpen = isSectionExpanded(nodePort, sectionKey);
    return (
      <div className="collapsible-section">
        <div className="collapsible-header" onClick={() => toggleSection(nodePort, sectionKey)}>
          <h4>{title}</h4>
          <span className={`toggle-icon ${isOpen ? 'open' : ''}`}>▼</span>
        </div>
        <div className={`collapsible-content ${isOpen ? 'open' : ''}`}>
          {content}
        </div>
      </div>
    );
  };

  const renderPreferences = (prefs) => {
    if (!prefs || Object.keys(prefs).length === 0) {
      return <div className="no-data">No preferences available</div>;
    }

    return (
      <div className="preferences-grid">
        {Object.entries(prefs).map(([key, value]) => (
          <div key={key} className="preference-item">
            <span className="info-label">{key}:</span>
            <span className="info-value">
              {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : 
               typeof value === 'object' ? JSON.stringify(value) : 
               String(value)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  const renderNodeCard = (node) => {
    const { port, owner, myInfo, metadata, ownerNode, meshNodes, preferences, modulePreferences } = node;
    const hasData = ownerNode || meshNodes?.length > 0;

    return (
      <div key={port} className="node-card">
        <div className="node-header">
          <div className="node-title">
            <h3>{owner || `Node ${myInfo?.myNodeNum || 'Unknown'}`}</h3>
            <span className="node-port-badge">Port: {port}</span>
          </div>
          <div className="node-status">
            <span className={`status-badge ${hasData ? 'online' : 'offline'}`}>
              {hasData ? 'Connected' : 'Offline'}
            </span>
          </div>
        </div>

        <div className="node-content">
          {/* System Info */}
          <div className="info-section">
            <h4>System Information</h4>
            <div className="info-grid">
              <span className="info-label">Node Number:</span>
              <span className="info-value">{myInfo?.myNodeNum || 'N/A'}</span>
              
              <span className="info-label">Firmware:</span>
              <span className="info-value">{metadata?.firmwareVersion || 'N/A'}</span>
              
              <span className="info-label">Hardware:</span>
              <span className="info-value">{metadata?.hwModel || 'N/A'}</span>
              
              <span className="info-label">Role:</span>
              <span className="info-value">{metadata?.role || 'N/A'}</span>
              
              <span className="info-label">Reboot Count:</span>
              <span className="info-value">{myInfo?.rebootCount ?? 'N/A'}</span>
            </div>
          </div>

          {/* Owner Node Info */}
          {ownerNode && (
            <div className="info-section">
              <h4>Owner Node Details</h4>
              <div className="info-grid">
                <span className="info-label">ID:</span>
                <span className="info-value">{ownerNode.id || 'N/A'}</span>
                
                <span className="info-label">Name:</span>
                <span className="info-value">
                  {ownerNode.user?.longName || 'N/A'} ({ownerNode.user?.shortName || 'N/A'})
                </span>
                
                <span className="info-label">MAC:</span>
                <span className="info-value">{ownerNode.user?.macaddr || 'N/A'}</span>
                
                {ownerNode.deviceMetrics?.batteryLevel !== undefined && (
                  <>
                    <span className="info-label">Battery:</span>
                    <span className="info-value">
                      {formatBattery(ownerNode.deviceMetrics.batteryLevel)}
                      <span className={`metric-badge ${getBatteryClass(ownerNode.deviceMetrics.batteryLevel)}`}>
                        {ownerNode.deviceMetrics.batteryLevel === 101 ? '⚡' : '🔋'}
                      </span>
                    </span>
                  </>
                )}
                
                {ownerNode.deviceMetrics?.uptimeSeconds !== undefined && (
                  <>
                    <span className="info-label">Uptime:</span>
                    <span className="info-value">{formatUptime(ownerNode.deviceMetrics.uptimeSeconds)}</span>
                  </>
                )}
                
                {ownerNode.deviceMetrics?.channelUtilization !== undefined && (
                  <>
                    <span className="info-label">Ch. Utilization:</span>
                    <span className="info-value">{ownerNode.deviceMetrics.channelUtilization.toFixed(2)}%</span>
                  </>
                )}
              </div>
              
              {ownerNode.position?.latitude && (
                <div className="position-info">
                  📍 {ownerNode.position.latitude.toFixed(6)}, {ownerNode.position.longitude.toFixed(6)}
                </div>
              )}
            </div>
          )}

          {/* Mesh Nodes */}
          {meshNodes && meshNodes.length > 0 && (
            <div className="mesh-nodes-section">
              <h4>Mesh Nodes ({meshNodes.length})</h4>
              <div className="mesh-nodes-grid">
                {meshNodes.map((meshNode) => (
                  <div key={meshNode.id} className="mesh-node-card">
                    <div className="mesh-node-header">
                      <span className="mesh-node-name">
                        {meshNode.user?.longName || `Node ${meshNode.num}`}
                      </span>
                      <span className="mesh-node-id">{meshNode.id}</span>
                    </div>
                    
                    <div className="mesh-node-details">
                      <span className="info-label">Short Name:</span>
                      <span className="info-value">{meshNode.user?.shortName || 'N/A'}</span>
                      
                      <span className="info-label">Hardware:</span>
                      <span className="info-value">{meshNode.user?.hwModel || 'N/A'}</span>
                      
                      {meshNode.hopsAway !== undefined && (
                        <>
                          <span className="info-label">Hops Away:</span>
                          <span className="info-value">
                            {meshNode.hopsAway}
                            <span className="hops-badge">{meshNode.hopsAway === 0 ? 'Direct' : `${meshNode.hopsAway} hop${meshNode.hopsAway > 1 ? 's' : ''}`}</span>
                          </span>
                        </>
                      )}
                      
                      {meshNode.snr !== undefined && (
                        <>
                          <span className="info-label">SNR:</span>
                          <span className="info-value">
                            {meshNode.snr.toFixed(2)} dB
                            <span className={`metric-badge ${getSnrClass(meshNode.snr)}`}>
                              {meshNode.snr >= -5 ? '📶' : meshNode.snr >= -12 ? '📡' : '📉'}
                            </span>
                          </span>
                        </>
                      )}
                    </div>
                    
                    {meshNode.position?.latitude && (
                      <div className="position-info">
                        📍 {meshNode.position.latitude.toFixed(6)}, {meshNode.position.longitude.toFixed(6)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Device Preferences */}
          {preferences?.device && renderCollapsibleSection(
            'Device Preferences',
            renderPreferences(preferences.device),
            port,
            'device-prefs'
          )}

          {/* LoRa Configuration */}
          {preferences?.lora && renderCollapsibleSection(
            'LoRa Configuration',
            renderPreferences(preferences.lora),
            port,
            'lora-config'
          )}

          {/* Module Preferences */}
          {modulePreferences && Object.keys(modulePreferences).length > 0 && renderCollapsibleSection(
            'Module Preferences',
            <div>
              {Object.entries(modulePreferences).map(([moduleName, moduleConfig]) => (
                <div key={moduleName} style={{ marginBottom: '15px' }}>
                  <h5 style={{ color: '#888', fontSize: '13px', marginBottom: '8px' }}>
                    {moduleName.toUpperCase()}
                  </h5>
                  {renderPreferences(moduleConfig)}
                </div>
              ))}
            </div>,
            port,
            'module-prefs'
          )}
        </div>
      </div>
    );
  };

  if (loading && nodesData.length === 0) {
    return (
      <div className="extended-node-view">
        <div className="loading-message">⏳ Loading Meshtastic nodes...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="extended-node-view">
        <div className="error-message">
          ❌ {error}
          <br />
          <button className="refresh-button" onClick={fetchNodes} style={{ marginTop: '15px' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="extended-node-view">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>🔌 Meshtastic Nodes - Extended View</h2>
        <button className="refresh-button" onClick={fetchNodes}>
          🔄 Refresh
        </button>
      </div>
      
      {nodesData.length === 0 ? (
        <div className="error-message">
          No nodes found. Make sure your Meshtastic nodes are running on the configured ports.
        </div>
      ) : (
        <div className="nodes-container">
          {nodesData.map(renderNodeCard)}
        </div>
      )}
    </div>
  );
};

export default ExtendedNodeView;
