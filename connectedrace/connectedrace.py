import can
import logger
import antenna

def main():
    can_interface = 'vcan0'
    bus = can.interface.Bus(can_interface, bustype='socketcan_native')
    # msg = can.Message(arbitration_id=0xc0ffee,
    #                   data=[0, 25, 0, 1, 3, 1, 4, 1],
    #                   extended_id=False)
    # if bus.send(msg):
    #     print("Message NOT sent")
    # else:
    #     print("Message sent")

    buffer = can.BufferedReader()
    csvlog = logger.CSVLogger('log.csv')
    sqlitelog = logger.SQLiteLogger('log.db')

    notifier = can.Notifier(bus, [buffer, csvlog, sqlitelog], 15)

    for msg in iter(buffer.get_message, None):
        print(msg)



if __name__ == "__main__":
    main()

