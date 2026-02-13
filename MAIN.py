from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from UTIL import *
from CONFIG import *
import CAN
import TABLE
import DIALOG
import GRAPHS
import threading


class Main:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        self.root.geometry("%dx%d" % (self.width * 0.5, self.height * 0.5))
        self.root.state("zoomed")
        self.dbc_file = "DBC/DBC_IGT_v00.dbc" if DEBUG_MODE else ""
        self.draw_toolbar()

    def draw_toolbar(self):
        toolBar = Menu(self.root)
        self.root.configure(menu=toolBar)
        fileMenu = Menu(toolBar)
        toolBar.add_cascade(label="File", menu=fileMenu)
        toolBar.add_cascade(label="About", command=lambda: self.about())
        fileMenu.add_command(label="Import DBC", command=lambda: self.import_dbc())
        tabControl = ttk.Notebook(self.root)
        self.tab1 = ttk.Frame(tabControl)
        self.tab2 = ttk.Frame(tabControl)
        self.tab3 = ttk.Frame(tabControl)
        # self.draw_rx_graphs(self.tab1)
        self.draw_rx_table(self.tab2)
        self.draw_tx_table(self.tab3)

        tabControl.add(self.tab1, text="Rx_Graph")
        tabControl.add(self.tab2, text="Rx")
        tabControl.add(self.tab3, text="Tx")
        tabControl.pack(expand=1, fill="both")

    def draw_rx_table(self, frame):
        self.rx_table = TABLE.PandasTable(frame, self.height, self.width)

    def draw_tx_table(self, frame):
        self.tx_table = TABLE.PandasTable(frame, self.height, self.width)

    def draw_rx_graphs(self, frame, db):
        self.rx_graphs = GRAPHS.Graphs(frame, db)

    def import_dbc(self):
        self.dbc_file = askopenfilename()
        can_init(self.dbc_file, main.rx_table)

    def about(self):
        DIALOG.MessageBox(
            self.root,
            title=f"{APP_NAME} v{VERSION}",
            text="This software supports CAN .dbc parsing, simulated messages transmission and received messages interpretation.",
            class_=None,
            buttons=["OK"],
            default=None,
            cancel=None,
        )


def can_init(main):
    can = CAN.Can()
    if not can.load_dbc(main.dbc_file):
        DIALOG.MessageBox(
            root,
            title="Import Failed",
            text=f"Selected File: {main.dbc_file}",
            class_=None,
            buttons=["OK"],
            default=None,
            cancel=None,
        )

    main.draw_rx_graphs(main.tab1, can.db)
    can.connect_bus()
    can.attach_listener(main.rx_table, main.rx_graphs)
    can.generate_can_messages()
    tx_thread = threading.Thread(
        target=can.transmit_can_messages, args=(can.generated_can_messages, main.tx_table)
    )
    tx_thread.start()
    # can.cleanup()


if __name__ == "__main__":
    root = Tk()
    main = Main(root)
    can_init(main)
    root.mainloop()
