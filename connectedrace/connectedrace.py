import can
import logger
import antenna
import cable
import time

def main():
    #
    # pseudocode for main:
    #
    # can_interfaces = ['vcan0'] # TODO: scan system for interfaces, don't hardcode
    # serve_port = 5252
    # logfiles = ['log.csv', 'log.db'] # TODO: loggings have to be created per run, CSV doesn't yet
    #
    # cableslave = cable.Handler(can_interfaces)
    # antennaslave = antenna.Handler(serve_port)
    # loggingslave = logger.Handler(logfiles)
    #
    # cableslave.shoot(list_of(antennaslave.targets, loggingslave.targets))
    # antennaslave.shoot(list_of(cableslave.targets, loggingslave.targets))
    #
    # massacre(cableslave, antennaslave, loggingslave)
    #

    msglist = [ can.Message(arbitration_id=0xc0ffee,
                            data=[0, 25, 0, 1, 3, 1, 4, 1],
                            extended_id=False) ]

    cabled = cable.CableDaemon()

    buffer = can.BufferedReader()
    csv_logger = logger.CSVLogger('log.csv')
    listeners = [buffer, csv_logger]
    # sqlitelog = logger.SQLiteLogger('log.db')
    for l in listeners:
        cabled.add_listener(l)

    while(True):
        msg = buffer.get_message()
        if msg is not None:
            print(msg)
        if cabled(msglist):
            print("Message NOT sent")
        else:
            print("Message sent")

if __name__ == "__main__":
    main()

