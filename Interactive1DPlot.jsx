import React, { useRef, useState, useEffect, forwardRef, useImperativeHandle } from "react";

const Interactive1DPlot = forwardRef(({ xmin = 0, xmax = 10, width = 600, height = 150 }, ref) => {
  const canvasRef = useRef(null);

  // state
  const [range, setRange] = useState({ xmin, xmax });
  const [axisOffset, setAxisOffset] = useState(0);
  const [markers, setMarkers] = useState([]);
  const [zoomMode, setZoomMode] = useState(false);
  const [dragStart, setDragStart] = useState(null);
  const [legendPos, setLegendPos] = useState({ x: width - 160, y: 10 });
  const [title, setTitle] = useState("");
  const [panStart, setPanStart] = useState(null);

  // expose methods to parent (MultiPlotManager)
  useImperativeHandle(ref, () => ({
    addMarker: (value, color = "red", label = "marker") => {
      setMarkers((prev) => [...prev, { value, color, label }]);
    },
    setTitle: (t) => setTitle(t),
    getCanvas: () => canvasRef.current,
    resetView: () => {
      setRange({ xmin, xmax });
      setAxisOffset(0);
    },
    toggleZoomMode: () => setZoomMode((z) => !z),
  }));

  // redraw on state change
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, width, height);

    // axis
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();

    // ticks
    const span = range.xmax - range.xmin;
    const step = span / 6;
    for (let x = range.xmin; x <= range.xmax; x += step) {
      const pos = mapToCanvas(x, range, width) + axisOffset;
      ctx.beginPath();
      ctx.moveTo(pos, height / 2 - 10);
      ctx.lineTo(pos, height / 2 + 10);
      ctx.stroke();
      ctx.fillText(x.toFixed(2), pos, height / 2 + 20);
    }

    // markers
    markers.forEach(({ value, color }) => {
      const pos = mapToCanvas(value, range, width) + axisOffset;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(pos, height / 2, 5, 0, 2 * Math.PI);
      ctx.fill();
    });

    // legend
    if (markers.length > 0) {
      ctx.strokeRect(legendPos.x, legendPos.y, 150, 20 + markers.length * 15);
      ctx.fillText("Legend", legendPos.x + 10, legendPos.y + 15);
    }

    // title
    if (title) {
      ctx.font = "14px Arial";
      ctx.textAlign = "center";
      ctx.fillText(title, width / 2, 20);
    }
  }, [range, axisOffset, markers, legendPos, title, width, height]);

  // helpers
  const mapToCanvas = (value, range, width) =>
    ((value - range.xmin) / (range.xmax - range.xmin)) * width;

  const mapToValue = (xPixel, range, width) =>
    range.xmin + (xPixel / width) * (range.xmax - range.xmin);

  // unified mouse handlers
  const handleMouseDown = (e) => {
    if (e.button === 1) { // middle mouse → pan
      setPanStart(e.nativeEvent.offsetX);
    } else if (zoomMode && e.button === 0) { // left mouse → zoom drag
      setDragStart(e.nativeEvent.offsetX);
    }
  };

  const handleMouseMove = (e) => {
    if (panStart !== null) {
      const dx = e.nativeEvent.offsetX - panStart;
      setAxisOffset((prev) => prev + dx);
      setPanStart(e.nativeEvent.offsetX);
    }
  };

  const handleMouseUp = (e) => {
    if (panStart !== null) {
      setPanStart(null);
    }
    if (zoomMode && dragStart !== null) {
      const x1 = dragStart;
      const x2 = e.nativeEvent.offsetX;
      const v1 = mapToValue(Math.min(x1, x2), range, width);
      const v2 = mapToValue(Math.max(x1, x2), range, width);
      setRange({ xmin: v1, xmax: v2 });
      setDragStart(null);
      setZoomMode(false); // auto-disable
    }
  };

  // wheel zoom
  const handleWheel = (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 0.9 : 1.1;
    const center = (range.xmin + range.xmax) / 2;
    const span = (range.xmax - range.xmin) * zoomFactor;
    setRange({ xmin: center - span / 2, xmax: center + span / 2 });
  };

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{ border: "1px solid black" }}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onDoubleClick={() => {
        setRange({ xmin, xmax });
        setAxisOffset(0);
      }}
    />
  );
});

export default Interactive1DPlot;
