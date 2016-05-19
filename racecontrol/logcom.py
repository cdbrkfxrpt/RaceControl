# RaceControl, a bidirectional CAN bus telemetry platform.
# Copyright (C) 2016 Florian Eich

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import re
import socket
import arrow
import time
import can

from racecontrol.globals import DEVICE, CAN_IFACE, LOGDIR, FILEFORMAT


class LogCom:
    """Instatiates CSVLogger objects with user defined timestamps as filename
    patterns.

    The LogCom class, when instantiated, parses the input strings containing
    the timestamping patterns for the logging filename through the arrow
    library, which provides beautifully formatted strings with timestamps. It
    then creates a CSVLogger object it uses to log messages to a file.
    """
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

        fileformat += '-' + socket.gethostname()

        self.fileformat = fileformat

        self.csv_logger = CSVLogger(self.device,
                                    self.interface,
                                    self.fileformat + '.csv')

    def loggers(self):
        """
        Function which returns the current loggers owned by the LogCom object.
        The main function of the RaceControl package loops through this and
        distributes the objects to the other application members. Loggers have
        to implement the can.Listener interface for this to work.
        """
        return [self.csv_logger]


class CSVLogger(can.Listener):
    """Implements the can.Listener interface and writes messages in RaceControl
    CSV files.

    This class implements the can.Listener interface, which makes it callable
    from objects of the can.Notifier class with can.Message objects. On
    instantiation, it sets a timeout counter for flushing to file in case the
    file is downloaded intermittently and opens a file with user defined
    filename.
    """
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
        """
        Implements can.Listener's on_message_received method. Then proceeds to
        join all elements in the can.Message object it gets passed into a
        RaceControl CSV string and writes the string to file.
        """
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
        """
        Standard method called when the interpreter's garbage collector picks
        the object up. Since data is flushed via timeout and the garbage
        collector should close the open file object eventually as well, this is
        not technically necessary, but added for safety.
        """
        self.file.close()
