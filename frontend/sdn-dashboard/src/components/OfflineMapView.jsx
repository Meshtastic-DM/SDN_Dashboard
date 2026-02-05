// src/components/OfflineMapView.jsx
import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './OfflineMapView.css';

// Fix for default marker icon in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

// Custom cyan marker icon for nodes
const createCustomIcon = (label) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div class="marker-container">
        <div class="marker-circle"></div>
        <div class="marker-label">${label}</div>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
  });
};

// LocationMarker component to track user location
function LocationMarker() {
  const [position, setPosition] = React.useState(null);
  const map = useMapEvents({
    click() {
      map.locate();
    },
    locationfound(e) {
      setPosition(e.latlng);
      map.flyTo(e.latlng, map.getZoom());
    },
  });

  return position === null ? null : (
    <Marker position={position}>
      <Popup>You are here</Popup>
    </Marker>
  );
}

const OfflineMapView = ({ graphData }) => {
  const defaultCenter = [6.9271, 79.8612]; // Colombo, Sri Lanka as default
  const defaultZoom = 13;

  const nodes = useMemo(() => {
    if (graphData && graphData.nodes) {
      // Convert nodes to have lat/lon coordinates
      const baseLatitude = 6.9271;
      const baseLongitude = 79.8612;
      const spread = 0.01; // degrees

      return graphData.nodes.map((node, index) => {
        const angle = (2 * Math.PI * index) / graphData.nodes.length;
        const radius = spread;
        
        return {
          ...node,
          lat: baseLatitude + radius * Math.cos(angle),
          lon: baseLongitude + radius * Math.sin(angle),
        };
      });
    }
    return [];
  }, [graphData]);

  if (nodes.length === 0) {
    return (
      <div className="offline-map-container">
        <div className="view-placeholder">Loading map data...</div>
      </div>
    );
  }

  return (
    <div className="offline-map-container">
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <LocationMarker />
        
        {nodes.map((node) => (
          <Marker
            key={node.id}
            position={[node.lat, node.lon]}
            icon={createCustomIcon(node.name)}
          >
            <Popup>
              <div className="node-popup">
                <h4>{node.name}</h4>
                <p><strong>ID:</strong> {node.id}</p>
                <p><strong>Location:</strong> {node.lat.toFixed(4)}, {node.lon.toFixed(4)}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default OfflineMapView;
