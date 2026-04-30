import React, { useRef, useEffect } from "react";
import MultiPlotManager from "./MultiPlotManager";

function App() {
  const managerRef = useRef(null);

  // Example: add markers after mount
  useEffect(() => {
    if (managerRef.current) {
      // Access the first subplot and add a marker
      const firstPlot = managerRef.current.getPlot(0);
      if (firstPlot) {
        firstPlot.addMarker(5, "red", "Center");
        firstPlot.setTitle("First Plot");
      }

      // Access the second subplot
      const secondPlot = managerRef.current.getPlot(1);
      if (secondPlot) {
        secondPlot.addMarker(2, "blue", "Left");
        secondPlot.setTitle("Second Plot");
      }
    }
  }, []);

  return (
    <div>
      <h1>Multi Plot Demo</h1>
      {/* Manager with 2 rows, 2 columns */}
      <MultiPlotManager ref={managerRef} rows={2} cols={2} width={800} height={400} />
    </div>
  );
}

export default App;
