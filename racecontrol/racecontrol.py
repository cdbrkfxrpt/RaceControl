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

        configpath = os.path.expanduser('~/.config/racecontrol')
        if not os.path.exists(configpath):
            print('Creating ~/.config/racecontrol and copying default config.')
            os.makedirs(configpath)
            shutil.copy('etc/racecontrol.cfg', configpath)
            print('Success!')

        dbcpath = configpath + '/dbc'
        if not os.path.exists(dbcpath):
            print('''Creating ~/.config/racecontrol/dbc. Please place your DBC
                    files here.''')
            os.makedirs(dbcpath)

        blacklistdbc = im.importany(configpath + '/dbc/blacklist.dbc')
        prioritydbc = im.importany(configpath + '/dbc/priority.dbc')
        guiupperdbc = im.importany(configpath + '/dbc/guiupper.dbc')
        guilowerdbc = im.importany(configpath + '/dbc/guilower.dbc')
        guitextdbc = im.importany(configpath + '/dbc/guitext.dbc')

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