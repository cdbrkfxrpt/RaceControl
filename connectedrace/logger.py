import can
import datetime

class Logger(object):
    def __init__(self, filename, canbufferedreader):
        self.file = open(filename, 'wt')
        self.buf = canbufferedreader
        self.file.write('''
            timestamp,
            is_remote_frame,
            id_type,
            is_error_frame,
            arbitration_id,
            dlc,
            data\n
        ''')

    def logCSV():
        msg = self.buf.get_message()
        if msg is not None:
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
        self.file.write('\n')
        self.file.close()

