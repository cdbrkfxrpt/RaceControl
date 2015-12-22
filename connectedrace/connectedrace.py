import can
import time

def main():
    can_interface = 'vcan0'
    bus = can.interface.Bus(can_interface, bustype='socketcan_native')
    msg = can.Message(arbitration_id=0xc0ffee,
                      data=[0, 25, 0, 1, 3, 1, 4, 1],
                      extended_id=False)
    if bus.send(msg):
        print("Message NOT sent")
    else:
        print("Message sent")

    buffer = can.BufferedReader()
    printer = can.Printer()
    csvlog = CSVLogger('log.csv')
    sqlitelog = SQLiteLogger('log.db')

    notifier = can.Notifier(bus, [buffer, printer, csvwrite, sqlitewrite])

if __name__ == "__main__":
    main()
