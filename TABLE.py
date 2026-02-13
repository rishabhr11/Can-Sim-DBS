
from pandastable import Table
import pandas as pd
import tkinter as tk



class PandasTable:
    def __init__(self, frame, height, width):
        self.frame = tk.Frame(frame)
        self.frame.pack(padx=10, pady=10)
        self.df = pd.DataFrame(dict())
        self.table = Table(
            self.frame,
            dataframe=self.df,
            showtoolbar=True,
            showstatusbar=False,
            height=height,
            width=width,
            editable=False,
            enable_menus=False,
        )
        self.table.show()

    def insert_row(self, data):
        self.df = self.df._append(data, ignore_index=True)
        self.table.model.df = self.df
        # self.table.redraw()
