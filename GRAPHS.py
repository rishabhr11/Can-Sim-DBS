import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk

# import numpy as np
import tkinter as tk
from matplotlib.animation import FuncAnimation
import time


class Graphs:
    def __init__(self, frame, db):
        self.graphs_frame = frame
        self.graphs = dict()
        self.figure = Figure(figsize=(10, 10), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graphs_frame)
        self.db = db
        self.create_options()
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()
        self.graph_counter = 1
        self.signal_name_list = [
            signal.name
            for signal in self.db.get_message_by_name(self.options[0]).signals
        ]
        self.signal_range_dict = dict()
        for signal in self.db.get_message_by_name(self.options[0]).signals:
            self.signal_range_dict[signal.name] = (signal.minimum, signal.maximum)

    def add_signal_data(self, signal_name, data, unit):
        if signal_name in self.signal_name_list:
            # if graph does not exist; create
            if signal_name not in self.graphs:
                self.graphs[signal_name] = Graph(
                    signal_name,
                    unit,
                    self.figure,
                    self.graph_counter,
                    self.signal_range_dict[signal_name],
                )
                self.graph_counter = self.graph_counter + 1
            self.graphs[signal_name].update_graph(data)

    def create_options(self):
        self.options = [message.name for message in self.db.messages]
        self.dropdown = ttk.Combobox(master=self.graphs_frame, values=self.options)
        self.dropdown.bind("<<ComboboxSelected>>", self.select_option)
        self.dropdown.current(0)
        self.dropdown.place(x=950, y=50, anchor="n")

    def select_option(self, event):
        self.selected = self.dropdown.get()
        self.signal_name_list = [
            signal.name for signal in self.db.get_message_by_name(self.selected).signals
        ]
        self.signal_range_dict = dict()
        for signal in self.db.get_message_by_name(self.selected).signals:
            self.signal_range_dict[signal.name] = (signal.minimum, signal.maximum)
        for graph in self.graphs.values():
            graph.delete_plot()
            del graph
        self.graphs = dict()
        self.graph_counter = 1


class Graph:
    def __init__(self, signal_name, unit, figure, id, range):
        self.figure = figure
        self.unit = unit
        self.signal_name = signal_name
        self.id = id
        self.range = range
        # self.x = 0
        self.y = 0
        self.x_axes = []
        self.y_axes = []
        self.anim_running = True
        self.start_time = time.perf_counter_ns()
        self.axes = figure.add_subplot(2, 2, self.id)
        (self.line,) = self.axes.plot([], [])
        self.axes.set(
            ylim=self.range,
            xticks=[],
            ylabel=self.unit,
            title=self.signal_name,
        )
        # self.axes.set(xlim=(0, 10), ylim=(-100, 100), title=self.signal_name)
        # self.figure.canvas.mpl_connect("button_press_event", self.onClick)
        self.animation = FuncAnimation(
            self.figure, self.animate, init_func=self.init, interval=33, blit=True
        )

        # self.plot.plot(self.x_axes,self.y_axes)
        # self.plot.show()

    def init(self):
        self.line.set_data(self.x_axes, self.y_axes)
        return (self.line,)

    def delete_plot(self):
        
        self.figure.delaxes(self.axes)
        (self.animation).use_blit=False
        self.figure.clear()

    def update_graph(self, data):
        self.y = data

    def animate(self, i):
        duration_s = (time.perf_counter_ns() - self.start_time) / 1_000_000_000
        self.x_axes.append(duration_s)
        self.y_axes.append(self.y)
        if len(self.x_axes) > 20:
            self.x_axes.pop(0)
            self.y_axes.pop(0)
        # self.plot.clear()
        # self.plot.plot(self.x_axes, self.y_axes, label=self.signal_name)
        self.line.set_data(self.x_axes, self.y_axes)
        self.axes.set(xlim=(min(self.x_axes), max(self.x_axes)))
        # self.plot.legend()
        # self.plot.set_title(f"{self.y} {self.unit}")
        # self.plot.set_xlabel("Time")
        # self.plot.set_ylabel(self.unit)
        return (self.line,)

    # def onClick(self, event):
    #     if self.anim_running:
    #         self.animation.event_source.stop()
    #     else:
    #         self.animation.event_source.start()
    #     self.anim_running = not (self.anim_running)
