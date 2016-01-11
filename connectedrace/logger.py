import os, threading, sqlite3
import arrow, time
import can

class LoggingDaemon:
    def __init__(self, root='/home/flrn/ConnectedRaceData/'):
        if not os.path.exists(root):
            os.makedirs(root)
        os.chdir(root)
        self.csv_logger = CSVLogger('log.csv')
        self.sqlite_logger = SQLiteLogger('log.db')

    def loggers(self):
        return [self.csv_logger, self.sqlite_logger]

class CSVLogger(can.Listener):
    def __init__(self, filename):
        self.flushstamp = time.perf_counter()
        self.filename = filename
        self.file = open(self.filename, 'wt')
        self.file.write(
        'timestamp,is_remote_frame,id_type,\
is_error_frame,arbitration_id,dlc,data\n')

    def on_message_received(self, msg):
        print('Logging ', msg)
        row = ','.join(str(el) for el in [  msg.timestamp,
                                            msg.is_remote_frame,
                                            msg.id_type,
                                            msg.is_error_frame,
                                            msg.arbitration_id,
                                            msg.dlc,
                                            ''.join('%.2x' % byte
                                                for byte in msg.data)
                                         ])
        self.file.write(row + '\n')
        if time.perf_counter() - self.flushstamp > 1.0:
            self.file.flush()
            os.fsync(self.file.fileno())
            self.flushstamp = time.perf_counter()

    def __del__(self):
        self.file.close()


class SQLiteLogger(can.Listener):
    def __init__(self, filename):
        self.lock = threading.Lock()
        if not os.path.exists(filename):
            open(filename, 'w').close()
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.tablename = 'log' + arrow.now().format('YYYYMMDDD')
        header = '(timestamp, is_remote_frame, id_type, is_error_frame,\
                   arbitration_id, dlc, data)'
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS %s
                %s''' % (self.tablename, header))
        self.conn.commit()

    def on_message_received(self, msg):
        data = ''.join('%.2x' % byte for byte in msg.data)
        row = ','.join(str(el) for el in [msg.timestamp, msg.is_remote_frame,
                                          msg.is_error_frame,
                                          msg.arbitration_id, msg.dlc, data])
        set = [ msg.timestamp, msg.is_remote_frame, msg.id_type,
                msg.is_error_frame, msg.arbitration_id, msg.dlc, data ]
        try:
            self.lock.acquire(True)
            self.cursor.execute('''INSERT INTO %s VALUES (?, ?, ?, ?, ?, ?, ?)'''
                                % self.tablename, set)
            self.conn.commit()
        finally:
            self.lock.release()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
