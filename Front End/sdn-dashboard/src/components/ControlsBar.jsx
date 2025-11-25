// src/components/ControlsBar.js
import React from "react";

const ControlsBar = ({ entryCount, onReset, loading, error }) => {
  return (
    <div
      style={{
        display: "flex",
        gap: 8,
        marginBottom: 12,
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      <button
        onClick={onReset}
        style={{
          padding: "6px 12px",
          borderRadius: 999,
          border: "1px solid #4b5563",
          background: "#111827",
          color: "#e5e7eb",
          cursor: "pointer",
          fontSize: 13,
        }}
      >
        Reset simulation
      </button>

      <span style={{ fontSize: 13, color: "#9ca3af" }}>
        Entries loaded: <strong>{entryCount}</strong>
      </span>

      {loading && (
        <span style={{ fontSize: 13, color: "#fbbf24" }}>Loading...</span>
      )}

      {error && (
        <span style={{ fontSize: 13, color: "#f97373" }}>
          Backend error (check console)
        </span>
      )}
    </div>
  );
};

export default ControlsBar;
