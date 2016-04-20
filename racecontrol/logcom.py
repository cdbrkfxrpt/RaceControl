# RaceControl, a bidirectional CAN bus telemetry platform.
# Copyright (C) 2016 Florian Eich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import re
import socket
import arrow
import time
import can

from racecontrol.globals import DEVICE, CAN_IFACE, LOGDIR, FILEFORMAT


class LogCom:
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

        self.device = DEVICE
        self.interface = CAN_IFACE

        if os.geteuid() == 0:
            self.logdir = '/var/www/loggings/' + logdir + '/'
        else:
            self.logdir = os.path.expanduser('~') + '/' + logdir + '/'

        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)

        os.chdir(self.logdir)

        fileformat += '-' + CAN_IFACE
        fileformat += '-' + socket.gethostname()

        self.fileformat = fileformat

        self.csv_logger = CSVLogger(self.device,
                                    self.interface,
                                    self.fileformat + '.csv')

    def loggers(self):
        return [self.csv_logger]


class CSVLogger(can.Listener):
    def __init__(self, device, interface, filename):
        self.device = device
        self.interface = interface
        self.flushstamp = time.perf_counter()
        self.filename = filename
        self.file = open(self.filename, 'wt')
        self.file.write(
        'device,interface,timestamp,is_remote_frame,id_type,\
is_error_frame,arbitration_id,dlc,data\n')

    def on_message_received(self, msg):
        row = ','.join(str(el) for el in [self.device,
                                          self.interface,
                                          msg.timestamp,
                                          msg.is_remote_frame,
                                          msg.id_type,
                                          msg.is_error_frame,
                                          msg.arbitration_id,
                                          msg.dlc,
                                          ''.join('%.2x' % byte
                                                  for byte in msg.data)])
        self.file.write(row + '\n')
        if time.perf_counter() - self.flushstamp > 1.0:
            self.file.flush()
            os.fsync(self.file.fileno())
            self.flushstamp = time.perf_counter()

    def __del__(self):
        self.file.close()
