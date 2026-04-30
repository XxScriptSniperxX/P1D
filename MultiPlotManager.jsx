import React, { useRef, forwardRef, useImperativeHandle } from "react";
import Interactive1DPlot from "./Interactive1DPlot";
import html2canvas from "html2canvas";

const MultiPlotManager = forwardRef(({ rows = 2, cols = 1, width = 800, height = 400 }, ref) => {
  const plotRefs = useRef([]);

  // expose methods to parent (App.jsx)
  useImperativeHandle(ref, () => ({
    getPlot: (index) => plotRefs.current[index] || null,
    saveAll: () => {
      plotRefs.current.forEach((plot, i) => {
        if (plot) {
          const canvas = plot.getCanvas();
          const link = document.createElement("a");
          link.download = `plot_${i + 1}.png`;
          link.href = canvas.toDataURL("image/png");
          link.click();
        }
      });
    },
    saveFrame: () => {
      const frame = document.getElementById("subplot-frame");
      html2canvas(frame).then((canvas) => {
        const link = document.createElement("a");
        link.download = "subplots_snapshot.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
      });
    },
  }));

  // create grid of plots
  const subplots = [];
  const sub_h = height / rows;
  const sub_w = width / cols;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const idx = r * cols + c;
      subplots.push(
        <Interactive1DPlot
          key={idx}
          ref={(el) => (plotRefs.current[idx] = el)}
          xmin={0}
          xmax={10}
          width={sub_w}
          height={sub_h}
        />
      );
    }
  }

  return (
    <div>
      <div
        id="subplot-frame"
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gap: "10px",
          width,
          height,
        }}
      >
        {subplots}
      </div>
      <button onClick={() => ref.current.saveAll()}>Download All Plots</button>
      <button onClick={() => ref.current.saveFrame()}>Snapshot Subplots Only</button>
    </div>
  );
});

export default MultiPlotManager;
