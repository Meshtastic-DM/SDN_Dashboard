// src/components/Header.jsx
import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-left">
        <div className="logo">
          <span>Mesh FYP</span>
        </div>
        <h1 className="header-title">SDN Dashboard for Central Control</h1>
      </div>
      <div className="profile-icon">
        <span>Profile</span>
      </div>
    </header>
  );
};

export default Header;
