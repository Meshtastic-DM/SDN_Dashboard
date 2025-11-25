// src/components/Layout.js
import React from "react";

const Layout = ({ children }) => {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#030712",
        color: "#e5e7eb",
        padding: "16px",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      }}
    >
      {children}
    </div>
  );
};

export default Layout;
