# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:29:25 2026

@tag: Xx_ScriptSniper_xX
@author: Albin
"""
import tkinter as tk
from PIL import ImageGrab

class Interactive1DPlot:
    def __init__(self, xmin=0, xmax=10, width=600, height=150):
        self.xmin, self.xmax = xmin, xmax
        self.orig_xmin, self.orig_xmax = xmin, xmax
        self.width, self.height = width, height

        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # state
        self.markers = []
        self.major_step = 1
        self.minor_count = 0
        self.drag_start = None
        self.zoom_rect = None
        self.pan_start = None
        self.axis_offset = 0

        # bindings
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Double-Button-1>", self.on_reset_view)

        # pan (middle mouse button)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_move)
        self.canvas.bind("<ButtonRelease-2>", self.on_pan_end)

        # zoom with mouse wheel
        self.canvas.bind("<MouseWheel>", self.on_zoom)   # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)     # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)     # Linux scroll down

        # drag‑zoom (left mouse button)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        
        # Add a Download button
        self.download_btn = tk.Button(self.root, text="Download Plot", command=self.save_png)
        self.download_btn.pack(side="bottom", pady=5)

    # ---------------- PAN ----------------
    def on_pan_start(self, event):
        self.pan_start = event.x

    def on_pan_move(self, event):
        if self.pan_start is not None:
            dx = event.x - self.pan_start
            self.axis_offset += dx
            self.pan_start = event.x
            self.redraw()

    def on_pan_end(self, event):
        self.pan_start = None

    # ---------------- ZOOM ----------------
    def on_zoom(self, event):
        zoom_factor = 0.9 if event.delta > 0 else 1.1
        center = (self.xmin + self.xmax) / 2
        span = (self.xmax - self.xmin) * zoom_factor
        self.xmin = center - span/2
        self.xmax = center + span/2
        self.redraw()

    # ---------------- RESET ----------------
    def on_reset_view(self, event=None):
        self.xmin, self.xmax = self.orig_xmin, self.orig_xmax
        self.axis_offset = 0
        self.redraw()

    # ---------------- DRAG-ZOOM ----------------
    def on_drag_start(self, event):
        self.drag_start = event.x
        if self.zoom_rect:
            self.canvas.delete(self.zoom_rect)
            self.zoom_rect = None

    def on_drag_move(self, event):
        if self.drag_start is not None:
            if self.zoom_rect:
                self.canvas.delete(self.zoom_rect)
            self.zoom_rect = self.canvas.create_rectangle(
                self.drag_start, 0, event.x, self.height,
                outline="blue", dash=(2,2)
            )

    def on_drag_end(self, event):
        if self.drag_start is not None:
            x1, x2 = sorted([self.drag_start, event.x])
            v1, v2 = self.map_to_value(x1), self.map_to_value(x2)
            if abs(v2 - v1) > 1e-6:
                self.xmin, self.xmax = v1, v2
            self.drag_start = None
            if self.zoom_rect:
                self.canvas.delete(self.zoom_rect)
                self.zoom_rect = None
            self.redraw()

    # ---------------- DRAWING ----------------
    def map_to_canvas(self, value):
        return int((value - self.xmin) / (self.xmax - self.xmin) * self.width)

    def map_to_value(self, x_pixel):
        return self.xmin + (x_pixel / self.width) * (self.xmax - self.xmin)

    def draw_axis(self):
        self.canvas.create_line(0, self.height//2, self.width, self.height//2)

    def draw_ticks(self):
        min_ticks = 6
        span = self.xmax - self.xmin
        step = span / min_ticks
    
        # dynamic precision
        if span > 10:
            precision = 0
        elif span > 1:
            precision = 2
        elif span > 0.01:
            precision = 4
        else:
            precision = 6
    
        # Instead of looping only from xmin to xmax,
        # generate ticks across the entire canvas width
        # using the offset.
        # Find the first tick value that maps just left of the canvas
        start_value = self.xmin - (self.axis_offset / self.width) * span
        # Snap to nearest step
        start_value -= (start_value % step)
    
        # Loop until we cover the canvas width
        x = start_value
        while True:
            pos = self.map_to_canvas(x) + self.axis_offset
            if pos > self.width:
                break
            if pos >= 0:
                self.canvas.create_line(pos, self.height//2-10, pos, self.height//2+10)
                self.canvas.create_text(pos, self.height//2+20, text=f"{x:.{precision}f}")
                if self.minor_count > 0:
                    minor_step = step / (self.minor_count+1)
                    for i in range(1, self.minor_count+1):
                        minor_pos = self.map_to_canvas(x + i*minor_step) + self.axis_offset
                        if 0 <= minor_pos <= self.width:
                            self.canvas.create_line(minor_pos, self.height//2-5, minor_pos, self.height//2+5)
            x += step



    def draw_marker(self, value, color="red"):
        self.markers.append((value, color))
        pos = self.map_to_canvas(value) + self.axis_offset
        self.canvas.create_oval(pos-5, self.height//2-5, pos+5, self.height//2+5, fill=color)
        
    def redraw(self):
        self.canvas.delete("all")
        self.draw_axis()
        self.draw_ticks()
        for value, color, label in self.markers:   # ✔ expects 3 values
            pos = self.map_to_canvas(value) + self.axis_offset
            self.canvas.create_oval(pos-5, self.height//2-5, pos+5, self.height//2+5, fill=color)

    # ---------------- UTIL ----------------
    def on_resize(self, event):
        self.width, self.height = event.width, event.height
        self.redraw()

    # ---------------- Save ----------------
    def save_png(self, filename="plot.png"):
        # Grab the canvas region directly (no Ghostscript needed)
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        # Capture and save
        ImageGrab.grab().crop((x, y, x1, y1)).save(filename)
        print(f"Plot saved as {filename}")

    # ---------------- Show ----------------
    def show(self):
        self.redraw()
        self.root.mainloop()

# Example usage
if __name__ == "__main__":
    plot = Interactive1DPlot(0, 10)
    plot.major_step = 2
    plot.minor_count = 3
    plot.markers.append((4.5, "red", "Point A"))
    plot.markers.append((7.2, "blue", "Point B"))
    plot.show()
