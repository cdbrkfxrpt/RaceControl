import os, threading, re
import socket, sqlite3
import arrow, time
import can
from connectedrace.globals import CAN_IFACE, LOGDIR, FILEFORMAT

class LoggingDaemon:
    def __init__(self, logdir=LOGDIR, fileformat=FILEFORMAT):
        if not logdir:
            print('Please specify a valid log directory name.')
            sys.exit(1)

        if not fileformat:
            print('Please specify a valid file format.')
            sys.exit(1)

        timepat = re.compile(r'([(YY)MDdHhm:-]+)_')
        stamp = arrow.now()

        logdir_stamp = stamp.format(timepat.search(logdir).group(1))
        fileformat_stamp = stamp.format(timepat.search(fileformat).group(1))

        logdir = timepat.sub(logdir_stamp + '_', logdir)
        fileformat = timepat.sub(fileformat_stamp + '_', fileformat)

        if os.geteuid() == 0:
            self.logdir = '/var/tmp/' + logdir + '/'
        else:
            self.logdir = os.path.expanduser('~') + '/' + logdir + '/'

        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)

        os.chdir(self.logdir)

        fileformat += '-' + CAN_IFACE
        fileformat += '-' + socket.gethostname()

        self.fileformat = fileformat

        self.csv_logger = CSVLogger(self.fileformat + '.csv')
        self.sqlite_logger = SQLiteLogger(
                self.fileformat.split('_')[1] + '.sqlite',
                re.sub(r':', 'h', 'OUT_' + self.fileformat.split('_')[0])
        )

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
    def __init__(self, filename, tablename):
        self.lock = threading.Lock()
        if not os.path.exists(filename):
            open(filename, 'w').close()
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.tablename = tablename
        header = '(timestamp, is_remote_frame, id_type, is_error_frame,\
                   arbitration_id, dlc, data)'
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS %s %s''' % (self.tablename, header)
        )
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
