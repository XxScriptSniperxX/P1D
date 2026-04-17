# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:29:25 2026

@tag: Xx_ScriptSniper_xX

@author: Albin
"""
import tkinter as tk

class Interactive1DPlot:
    def __init__(self, xmin=0, xmax=10, width=600, height=150):
        self.xmin, self.xmax = xmin, xmax
        self.width, self.height = width, height
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.orig_xmin, self.orig_xmax = xmin, xmax
        self.pan_start = None
        self.axis_offset = 0


        # state
        self.markers = []
        self.major_step = 1
        self.minor_count = 0
        self.drag_start = None
        self.zoom_rect = None
        self.pan_start = None   # separate state for panning
    
        # bindings
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Double-Button-1>", self.on_reset_zoom)
    
        # pan (mouse scroll wheel hold = Button-2)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_move)
        self.pan_velocity = 0
        self.is_scrolling = False
        self.canvas.bind("<ButtonRelease-2>", self.on_pan_end)


        # zoom with mouse wheel
        self.canvas.bind("<MouseWheel>", self.on_zoom)   # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)     # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)     # Linux scroll down
    
        # drag‑zoom (left mouse button)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
    
        # pan (right mouse button)
        self.canvas.bind("<ButtonPress-3>", self.on_pan_start)
        self.canvas.bind("<B3-Motion>", self.on_pan_move)
            
    def on_pan_start(self, event):
        self.pan_start = event.x
    
    def on_pan_move(self, event):
        if self.pan_start is not None:
            dx = event.x - self.pan_start
            # convert pixel shift into value shift
            shift = dx / self.width * (self.xmax - self.xmin)
            # shift the entire axis range
            self.xmin -= shift
            self.xmax -= shift
            self.pan_start = event.x
            self.redraw()


    def on_pan_end(self, event):
        # start momentum scroll
        self.is_scrolling = True
        self._scroll_step()
    
    def _scroll_step(self):
        if self.is_scrolling and abs(self.pan_velocity) > 1e-6:
            # apply velocity
            self.xmin -= self.pan_velocity
            self.xmax -= self.pan_velocity
            self.redraw()
            # decay velocity (friction)
            self.pan_velocity *= 0.9
            # schedule next step
            self.root.after(30, self._scroll_step)
        else:
            self.is_scrolling = False

    def on_reset_zoom(self, event=None):
        """Reset zoom to original axis range on double click."""
        self.xmin, self.xmax = self.orig_xmin, self.orig_xmax
        self.redraw()
        
    def on_drag_start(self, event):
        self.drag_start = event.x
        if self.zoom_rect:
            self.canvas.delete(self.zoom_rect)
            self.zoom_rect = None
    
    def on_drag_move(self, event):
        if self.drag_start is not None:
            if self.zoom_rect:
                self.canvas.delete(self.zoom_rect)
            # draw temporary zoom rectangle
            self.zoom_rect = self.canvas.create_rectangle(
                self.drag_start, 0, event.x, self.height,
                outline="blue", dash=(2,2)
            )
    
    def on_drag_end(self, event):
        if self.drag_start is not None:
            x1, x2 = sorted([self.drag_start, event.x])
            v1, v2 = self.map_to_value(x1), self.map_to_value(x2)
            if abs(v2 - v1) > 1e-6:  # avoid zero-width zoom
                self.xmin, self.xmax = v1, v2
            self.drag_start = None
            if self.zoom_rect:
                self.canvas.delete(self.zoom_rect)
                self.zoom_rect = None
            self.redraw()

    def map_to_canvas(self, value):
        return int((value - self.xmin) / (self.xmax - self.xmin) * self.width)

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
    
        x = self.xmin
        while x <= self.xmax:
            pos = self.map_to_canvas(x)
            self.canvas.create_line(pos, self.height//2-10, pos, self.height//2+10)
            self.canvas.create_text(pos, self.height//2+20, text=f"{x:.{precision}f}")
            # minor ticks
            if self.minor_count > 0:
                minor_step = step / (self.minor_count+1)
                for i in range(1, self.minor_count+1):
                    minor_pos = self.map_to_canvas(x + i*minor_step)
                    self.canvas.create_line(minor_pos, self.height//2-5, minor_pos, self.height//2+5)
            x += step
    
    def redraw(self):
        self.canvas.delete("all")
        self.draw_axis()
        self.draw_ticks()
        for value, color in self.markers:
            pos = self.map_to_canvas(value)
            self.canvas.create_oval(pos-5, self.height//2-5, pos+5, self.height//2+5, fill=color)


    def draw_marker(self, value, color="red"):
        self.markers.append((value, color))
        pos = self.map_to_canvas(value)
        self.canvas.create_oval(pos-5, self.height//2-5, pos+5, self.height//2+5, fill=color)

    # def redraw(self):
    #     self.canvas.delete("all")
    #     self.draw_axis()
    #     self.draw_ticks()
    #     for value, color in self.markers:
    #         pos = self.map_to_canvas(value) + self.axis_offset
    #         self.canvas.create_oval(pos-5, self.height//2-5, pos+5, self.height//2+5, fill=color)

    def on_resize(self, event):
        self.width, self.height = event.width, event.height
        self.redraw()

    def on_zoom(self, event):
        zoom_factor = 0.9 if event.delta > 0 else 1.1
        center = (self.xmin + self.xmax) / 2
        span = (self.xmax - self.xmin) * zoom_factor
        self.xmin = center - span/2
        self.xmax = center + span/2
        self.redraw()

    def on_pan_start(self, event):
        self.pan_start = event.x
    
    def on_pan_move(self, event):
        if self.pan_start is not None:
            dx = event.x - self.pan_start
            shift = dx / self.width * (self.xmax - self.xmin)
            self.xmin -= shift
            self.xmax -= shift
            self.pan_start = event.x
            self.redraw()

    def map_to_value(self, x_pixel):
        return self.xmin + (x_pixel / self.width) * (self.xmax - self.xmin)

    def save_png(self, filename="plot.ps"):
        # saves as PostScript (convert externally to PNG if needed)
        self.canvas.postscript(file=filename)

    def show(self):
        self.redraw()
        self.root.mainloop()


# Example usage
plot = Interactive1DPlot(0, 10)
plot.major_step = 2
plot.minor_count = 3
plot.draw_marker(4.5)
plot.draw_marker(7.2, color="blue")
plot.show()
