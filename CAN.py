import cantools
import can
import time
import threading
from UTIL import *
from CONFIG import *



lock=threading.Lock()

class Can:
    def __init__(self):
        self.generated_can_messages = []

    def load_dbc(self,dbc_file):
        if(dbc_file==""):
            print(f"{c.FAIL}Select a .dbc to load{c.ENDC}")
            return True
        try:
            self.db = cantools.db.load_file(dbc_file)
            print(f"{c.OKGREEN}Successfully imported .dbc file: {dbc_file}{c.ENDC}")    
            print(
                "############################# CAN DBC BEGIN #############################\n"
                + c.OKCYAN
            )
            print(self.db)
            print(
                c.ENDC + "############################# CAN DBC END #############################\n"
            )
            return True
        except:
            print(f"{c.FAIL}Can't import .dbc file: {dbc_file}{c.ENDC}")
            return False   
    def connect_bus(self):
        try:
            self.bus = can.interface.Bus(interface="pcan", channel="PCAN_USBBUS1", bitrate=500000)
            # self.bus = can.interface.Bus(interface="canalystii", channel='CAN0', bitrate=500000)
            # self.bus = can.interfaces.canalystii.CANalystIIBus(channel=0,)
        except:
            print(f"{c.FAIL}Can't connect to the CAN Interface!{c.ENDC}")

    def attach_listener(self,rx_table,graphs):
        try:
            self.notifier=can.Notifier(self.bus, [CANListener(self.db,rx_table,graphs)])
        except:
            print(f"{c.FAIL}Can't attach listener!{c.ENDC}")
            
    def generate_can_messages(self):
        self.no_of_values_in_msg_range = 100
        self.generated_can_messages = []
        for t in range(self.no_of_values_in_msg_range + 1):
            with lock:
                print(
                    "\n############################# ITERATION "
                    + str(t)
                    + " #############################\n"
                )
            for msg in self.db.messages:
                sim_signal_dict = dict()
                for signal in msg.signals:
                    if signal.length == 1:
                        sim_signal_dict[signal.name] = t % 2
                    else:
                        signal_step_size = (signal.maximum - signal.minimum) / self.no_of_values_in_msg_range
                        sim_signal_dict[signal.name] = int(
                            signal.minimum + signal_step_size * t
                        )
                with lock:
                    print(sim_signal_dict)
                payload = msg.encode(sim_signal_dict)
                self.generated_can_messages.append((msg.frame_id, payload))
                with lock:
                    print(
                        c.OKBLUE
                        + " ID: "
                        + hex(msg.frame_id)
                        + " DATA: 0x"
                        + "".join("{:02x}".format(x) for x in payload)
                        + " ~ "
                        + c.OKGREEN
                        + msg.name
                        + c.ENDC
                    )
        return self.generated_can_messages


    def transmit_can_messages(self,can_messages,tx_table):
        msg_count = 0
        err_count = 0
        while True:
            for msg in can_messages:
                msg = can.Message(
                    arbitration_id=msg[0], data=msg[1], is_extended_id=False, dlc=8
                )
                try:
                    if hasattr(self,"bus"):
                        self.bus.send(msg)
                        msg_count = msg_count + 1
                        msg_id=hex(msg.arbitration_id)
                        msg_data="".join("{:02x}".format(x) for x in msg.data)
                        with lock:
                            print(f"{c.OKGREEN}TX: {msg_id} => {msg_data}{c.ENDC}")
                        tx_table.insert_row({msg_id:msg_data})
                except can.CanError as e:
                    err_count = err_count + 1
                    with lock:
                        print(f"{c.FAIL}TX: {msg_id} => {msg_data} (Failed, CAN Error code: {e.error_code}){c.ENDC}")
                time.sleep(0.01)

    def cleanup(self):
        self.notifier.stop()
        self.bus.shutdown()


class CANListener(can.Listener):
    
    def __init__(self, db,rx_table,graphs):
        self.db = db
        self.rx_table = rx_table
        self.graphs = graphs
        self.message_ids_in_dbc=[message.frame_id for message in self.db.messages]
    
    def on_message_received(self,msg):
        if(msg.arbitration_id in self.message_ids_in_dbc):
            try:
                decoded_msg=self.db.decode_message(msg.arbitration_id, msg.data)
                with lock:
                    print(f"{c.OKBLUE}RX: {decoded_msg}{c.ENDC}")
                self.rx_table.insert_row(decoded_msg)
                for signal in self.db.get_message_by_frame_id(msg.arbitration_id).signals:
                    if(signal.length!=1):
                        self.graphs.add_signal_data(signal.name,decoded_msg[signal.name],signal.unit)
                
            except:
                with lock:
                    print(f"{c.FAIL}RX: {hex(msg.arbitration_id)} => {"".join("{:02x}".format(x) for x in msg.data)} (Decoding Error){c.ENDC}")

