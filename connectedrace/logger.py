import can
import arrow
import sqlite3


class CSVLogger(Listener):
    def __init__(self, filename):
        self.file = open(filename, 'wt')
        self.file.write('''
            timestamp,
            is_remote_frame,
            id_type,
            is_error_frame,
            arbitration_id,
            dlc,
            data\n
        ''')

    def on_message_received(self, msg):
        row = ','.join(str(el) for el in [  msg.timestamp,
                                            msg.is_remote_frame,
                                            msg.id_type,
                                            msg.is_error_frame,
                                            msg.arbitration_id,
                                            msg.dlc,
                                            ''.join('%.2x' % byte for byte in msg.data)
                                         ])
        self.file.write(row + '\n')

    def __del__(self):
        self.file.close()
        super().__del__()


class SQLiteLogger(Listener):
    def __init__(self, filename):
        if not os.path.exists(filename):
            file(filename, 'w').close()
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS %s
                            (timestamp, is_remote_frame, id_type, is_error_frame,
                            arbitration_id, dlc, data)''' % arrow.now().format('YYYY-MM-DD'))
        self.conn.commit()

    def on_message_received(self, msg):
        self.cursor.execute('''INSERT INTO %s VALUES
                            (%s, %s, %s, %s, %s, %s, %s)''' % (
                                    arrow.now().format('YYYY-MM-DD'),
                                    msg.timestamp,
                                    msg.is_remote_frame,
                                    msg.id_type,
                                    msg.is_error_frame,
                                    msg.arbitration_id,
                                    msg.dlc,
                                    ''.join('%.2x' % byte for byte in msg.data)
                                )
                           )
        self.conn.commit()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

