// src/components/Sidebar.jsx
import React from 'react';
import './Sidebar.css';

const Sidebar = ({ activeView, onViewChange }) => {
  const menuItems = [
    { id: 'offline-map', label: 'Offline Map View' },
    { id: 'extended-node', label: 'Extended Node View' },
    { id: 'topology', label: 'Topology View' },
    { id: 'messaging', label: 'Messaging' },
    { id: 'route-analysis', label: 'Route Analysis' },
    { id: 'placeholder1', label: '' },
    { id: 'placeholder2', label: '' },
    { id: 'placeholder3', label: '' },
    { id: 'placeholder4', label: '' },
    { id: 'placeholder1', label: '' },
    { id: 'placeholder2', label: '' },
    { id: 'placeholder3', label: '' },
    { id: 'placeholder4', label: '' },
    { id: 'placeholder1', label: '' },
    { id: 'placeholder2', label: '' },
    { id: 'placeholder3', label: '' },
    { id: 'placeholder4', label: '' },
  ];

  return (
    <div className="sidebar">
      {menuItems.map((item) => (
        <button
          key={item.id}
          className={`sidebar-item ${activeView === item.id ? 'active' : ''} ${!item.label ? 'empty' : ''}`}
          onClick={() => item.label && onViewChange(item.id)}
          disabled={!item.label}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
};

export default Sidebar;
