import os
import can
import arrow
import sqlite3

class Handler(object):
    def __init__(self, logfiles):
        for i in logfiles:
            pass

class CSVLogger(can.Listener):
    def __init__(self, filename):
        self.file = open(filename, 'wt')
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

    def __del__(self):
        self.file.close()


class SQLiteLogger(can.Listener):
    def __init__(self, filename):
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
        self.cursor.execute('''INSERT INTO %s VALUES (?, ?, ?, ?, ?, ?, ?)'''
                            % self.tablename, set)
        self.conn.commit()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

