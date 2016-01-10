import can
import logger
import antenna
import cable
import queue

def main():
    # msgq = queue.Queue()
    # msgq.put(can.Message(arbitration_id=0xc0ffee,
    #                         data=[0, 25, 0, 1, 3, 1, 4, 1],
    #                         extended_id=False))
    # msgq.put(can.Message(arbitration_id=0x248,
    #                         data=[0, 12, 4, 2, 0, 8, 4, 3],
    #                         extended_id=False))

    cabled = cable.CableDaemon()
    antennad = antenna.AntennaDaemon()
    loggingd = logger.LoggingDaemon()

    cabled.add_listener(antennad.cannon.buffer)
    antennad.add_listener(cabled.buffer)

    for listener in loggingd.loggers():
        cabled.add_listener(listener)
        antennad.add_listener(listener)

    while True:
        pass

    # buffer = can.BufferedReader()
    # csv_logger = logger.CSVLogger('log.csv')
    # # sqlitelog = logger.SQLiteLogger('log.db')
    # listeners = [buffer, csv_logger]
    # for l in listeners:
    #     cabled.add_listener(l)

    # while(True):
    #     msg = buffer.get_message()
    #     if msg is not None:
    #         print(msg)
    #     cabled(msgq)

if __name__ == "__main__":
    main()
