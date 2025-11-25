// src/components/TopologyGraph.js
import React from "react";
import ForceGraph2D from "react-force-graph-2d";

const TopologyGraph = ({ graphData }) => {
  return (
    <div
      style={{
        width: "100%",
        height: "600px",
        borderRadius: 16,
        border: "1px solid #1f2937",
        overflow: "hidden",
      }}
    >
      <ForceGraph2D
        graphData={graphData}
        backgroundColor="#020617"
        nodeLabel={(node) => node.name}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        linkWidth={(link) => 1 + (link.hopCount || 1) * 0.2}
        linkLabel={(link) =>
          `self → nextHop
self: ${link.source?.id ?? link.source}
nextHop: ${link.target?.id ?? link.target}
for dest: ${link.destId}
hops: ${link.hopCount}
seq: ${link.destSeqNum}`
        }
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12 / globalScale;
          const radius = 10;

          ctx.beginPath();
          ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
          ctx.fillStyle = "#4ade80";
          ctx.fill();
          ctx.lineWidth = 1;
          ctx.strokeStyle = "#111827";
          ctx.stroke();

          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "top";
          ctx.fillStyle = "#e5e7eb";
          ctx.fillText(label, node.x, node.y + radius + 2);
        }}
      />
    </div>
  );
};

export default TopologyGraph;
