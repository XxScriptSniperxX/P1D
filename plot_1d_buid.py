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

        # state
        self.markers = []
        self.major_step = 1
        self.minor_count = 0
        self.drag_start = None

        # bindings
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.on_zoom)   # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)     # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)     # Linux scroll down
        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)

    def map_to_canvas(self, value):
        return int((value - self.xmin) / (self.xmax - self.xmin) * self.width)

    def draw_axis(self):
        self.canvas.create_line(0, self.height//2, self.width, self.height//2)

    def draw_ticks(self):
        x = self.xmin
        while x <= self.xmax:
            pos = self.map_to_canvas(x)
            self.canvas.create_line(pos, self.height//2-10, pos, self.height//2+10)
            self.canvas.create_text(pos, self.height//2+20, text=str(round(x,2)))
            if self.minor_count > 0:
                step = self.major_step / (self.minor_count+1)
                for i in range(1, self.minor_count+1):
                    minor_pos = self.map_to_canvas(x + i*step)
                    self.canvas.create_line(minor_pos, self.height//2-5, minor_pos, self.height//2+5)
            x += self.major_step

    def draw_marker(self, value, color="red"):
        self.markers.append((value, color))
        pos = self.map_to_canvas(value)
        self.canvas.create_oval(pos-5, self.height//2-5, pos+5, self.height//2+5, fill=color)

    def redraw(self):
        self.canvas.delete("all")
        self.draw_axis()
        self.draw_ticks()
        for value, color in self.markers:
            pos = self.map_to_canvas(value)
            self.canvas.create_oval(pos-5, self.height//2-5, pos+5, self.height//2+5, fill=color)

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
        self.drag_start = event.x

    def on_pan_move(self, event):
        if self.drag_start is not None:
            dx = event.x - self.drag_start
            shift = dx / self.width * (self.xmax - self.xmin)
            self.xmin -= shift
            self.xmax -= shift
            self.drag_start = event.x
            self.redraw()

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
