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
    # csvwrite = can.CSVWriter('log.csv')
    # sqlitewrite = can.SqliteWriter('log.sqlite')

    # notifier = can.Notifier(bus, [buffer, printer, csvwrite, sqlitewrite])
    i = 0
    while(i < 1):
        notifier = can.Notifier(bus, [buffer, printer])
        time.sleep(1)
        i += 1
    # notifier = can.Notifier(bus, [csvwrite])

    msg = buffer.get_message()

    print(msg , ' -- from buffer')

    f = open('log2.csv', 'wt')
    f.write('timestamp, is_remote_frame, id_type, is_error_frame, arbitration_id, dlc, data\n')
    row = ','.join(str(el) for el in [  msg.timestamp,
                                        msg.is_remote_frame,
                                        msg.id_type,
                                        msg.is_error_frame,
                                        msg.arbitration_id,
                                        msg.dlc,
                                        ''.join('%.2x' % byte for byte in msg.data)
                                     ])
    f.write(row + '\n')
    f.close()


if __name__ == "__main__":
    main()
