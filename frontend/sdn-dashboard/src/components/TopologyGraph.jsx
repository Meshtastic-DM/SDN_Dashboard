import React, { useMemo, useRef} from "react";
import ForceGraph2D from "react-force-graph-2d";
import './TopologyGraph.css';

const TopologyGraph = ({ graphData }) => {
  const fgRef = useRef();

  // Build a STATIC layout: put nodes on a circle and fix them with fx / fy
  const laidOutData = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] };

    const nodes = graphData.nodes || [];
    const links = graphData.links || [];
    const N = nodes.length;
    const radius = 100; // smaller spread of the circle

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

  // Center the graph and set appropriate zoom level
  // useEffect(() => {
  //   if (fgRef.current) {
  //     fgRef.current.centerAt(0, 0, 100);
  //     fgRef.current.zoom(1.5, 100);
  //   }
  // }, [laidOutData]);

  return (
    <div className="topology-container">
      <ForceGraph2D
        ref={fgRef}
        graphData={laidOutData}
        backgroundColor="transparent"
        nodeLabel={(node) => node.name}
        linkWidth={() => 2}
        linkColor={() => "rgba(0,0,0,0.3)"}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={0.9}
        // IMPORTANT: no simulation, no movement
        cooldownTicks={0}
        enableNodeDrag={false}
        enableZoomInteraction={true}
        enablePanInteraction={true}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12 / globalScale;
          const radius = 14;

          // Draw node circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
          ctx.fillStyle = "#22d3ee";
          ctx.fill();
          ctx.lineWidth = 2;
          ctx.strokeStyle = "#333";
          ctx.stroke();

          // Draw label background
          ctx.font = `bold ${fontSize}px Sans-Serif`;
          const labelWidth = ctx.measureText(label).width;
          const labelHeight = fontSize + 4;
          const labelX = node.x + radius + 6;
          const labelY = node.y - labelHeight / 2;

          ctx.fillStyle = "#fbbf24";
          ctx.fillRect(labelX, labelY, labelWidth + 8, labelHeight);
          ctx.strokeStyle = "#333";
          ctx.lineWidth = 1.5;
          ctx.strokeRect(labelX, labelY, labelWidth + 8, labelHeight);

          // Draw label text
          ctx.font = `bold ${fontSize}px Sans-Serif`;
          ctx.textAlign = "left";
          ctx.textBaseline = "middle";
          ctx.fillStyle = "#000";
          ctx.fillText(label, labelX + 4, node.y);
        }}
      />
    </div>
  );
};

export default TopologyGraph;
