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

import sys
import os
import shutil
import canmatrix.importany as im
import gevent.wsgi as wsgi

import racecontrol.logcom as logcom
import racecontrol.netcom as netcom
import racecontrol.cancom as cancom
import racecontrol.webcom as webcom


class RaceControl:
    """Central RaceControl application.

    Here, the run() method is located, which starts RaceControl.
    """
    def __init__(self):
        print(
            """
            RaceControl  Copyright (C) 2016  Florian Eich
            This program comes with ABSOLUTELY NO WARRANTY.
            This is free software, and you are welcome to
            redistribute it under certain conditions; see
            GPLv3 for details.
            """
        )

        # configpath = os.path.expanduser('~/.config/racecontrol')
        configpath = '/home/flrn/.config/racecontrol'
        if not os.path.exists(configpath):
            print('Creating ~/.config/racecontrol and copying default config.')
            os.makedirs(configpath)
            shutil.copy('etc/racecontrol.cfg', configpath)
            print('Success!')

        dbcpath = configpath + '/dbc'
        if not os.path.exists(dbcpath):
            print('Creating ~/.config/racecontrol/dbc.')
            os.makedirs(dbcpath)

        try:
            blacklistdbc = im.importany(dbcpath + '/blacklist.dbc')
            prioritydbc = im.importany(dbcpath + '/priority.dbc')
            guiupperdbc = im.importany(dbcpath + '/guiupper.dbc')
            guilowerdbc = im.importany(dbcpath + '/guilower.dbc')
            guitextdbc = im.importany(dbcpath + '/guitext.dbc')
        except FileNotFoundError:
            pass

        blacklist = [frame._Id for frame in blacklistdbc._fl._list]
        priority = [frame._Id for frame in prioritydbc._fl._list]

        msgfilter = {}

        upperid = guiupperdbc._fl._list[0]._Id
        lowerid = guilowerdbc._fl._list[0]._Id
        textid = guitextdbc._fl._list[0]._Id

        msgfilter[upperid] = {}
        msgfilter[lowerid] = {}
        msgfilter[textid] = {}

        offset = 0

        uppersignals = guiupperdbc._fl._list[0]._signals
        for sig in uppersignals:
            msgfilter[upperid][offset] = {}
            msgfilter[upperid][offset]['start'] = int(sig._startbit / 8)
            msgfilter[upperid][offset]['size'] = int(sig._signalsize / 8)
            msgfilter[upperid][offset]['name'] = sig._name
            offset += 1

        lowersignals = guilowerdbc._fl._list[0]._signals
        for sig in lowersignals:
            msgfilter[lowerid][offset] = {}
            msgfilter[lowerid][offset]['start'] = int(sig._startbit / 8)
            msgfilter[lowerid][offset]['size'] = int(sig._signalsize / 8)
            msgfilter[lowerid][offset]['name'] = sig._name
            offset += 1

        textsignals = guitextdbc._fl._list[0]._signals
        for sig in textsignals:
            msgfilter[textid][offset] = {}
            msgfilter[textid][offset]['start'] = int(sig._startbit / 8)
            msgfilter[textid][offset]['size'] = int(sig._signalsize / 8)
            msgfilter[textid][offset]['name'] = sig._name
            offset += 1

        self.cancomd = cancom.CANCom(blacklist)
        self.netcomd = netcom.NetCom(priority)
        self.logcomd = logcom.LogCom()
        self.webcomd = webcom.WebCom()
        self.guicomd = webcom.GUICom(self.webcomd.msgqueue, msgfilter)

        self.cancomd.add_listener(self.netcomd.dispatcher.buffer)
        self.cancomd.add_listener(self.guicomd.buffer)
        self.netcomd.add_listener(self.cancomd.buffer)

        for listener in self.logcomd.loggers():
            self.cancomd.add_listener(listener)
            self.netcomd.add_listener(listener)

    def run(self):
        """
        Main method of the RaceControl application. From here, the
        configuration files are read and all objects are created and connected
        and the server for the web application is started. This script is
        installed on the target machine's /usr/local/bin and can then be
        executed from the command line. Be sure to execute racecontrol as
        superuser so the /var/www/loggings directory is writable to store
        loggings under.
        """
        try:
            self.webcomd.app.debug = True
            server = wsgi.WSGIServer(("", 5000), self.webcomd.app)
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nExiting RaceControl.')
            sys.exit(0)
