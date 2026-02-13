import tkinter as tk
from tkinter import simpledialog


class MessageBox(simpledialog.SimpleDialog):
    def __init__(self, master, **kwargs):
        simpledialog.SimpleDialog.__init__(self, master, **kwargs)

    def done(self, num):
        self.num = num
        self.root.destroy()
