import React, { useMemo } from "react";
import ForceGraph2D from "react-force-graph-2d";

const TopologyGraph = ({ graphData }) => {
  // Build a STATIC layout: put nodes on a circle and fix them with fx / fy
  const laidOutData = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] };

    const nodes = graphData.nodes || [];
    const links = graphData.links || [];
    const N = nodes.length;
    const radius = 150; // spread of the circle

    const laidOutNodes = nodes.map((node, i) => {
      if (N === 0) return node;
      const angle = (2 * Math.PI * i) / N;
      return {
        ...node,
        // fixed positions – d3 will not move them
        fx: radius * Math.cos(angle),
        fy: radius * Math.sin(angle),
      };
    });

    return { nodes: laidOutNodes, links };
  }, [graphData]);

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
        graphData={laidOutData}
        backgroundColor="#020617"
        nodeLabel={(node) => node.name}
        linkWidth={() => 2.5}
        linkColor={() => "rgba(255,255,255,0.8)"}
        linkDirectionalArrowLength={8}
        linkDirectionalArrowRelPos={0.9}
        // IMPORTANT: no simulation, no movement
        cooldownTicks={0}
        enableNodeDrag={false}
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
