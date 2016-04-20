# CAN_IFACE specifies the name of the socketcan interface. This will be
# something like 'slcan0' or 'can0', depending what technology you use.
# SerialCAN uses 'slcan0', 'slcan1' and so on; the Linux Kernel Module for
# MCP251x over SPI tends to use 'can0', 'can1' and so on. If you have more than
# one CAN interface you want to log, run several ConnectedRace instances (or
# contact me at florian.eich@gmail.com, chances are I will help you out).
# 'vcan0' is the Linux virtual CAN interface used for testing.
DEVICE = 'PWe6.15'
CAN_IFACE = 'vcan0'

# NODES specifies the IP addresses of your other nodes. Leave empty ([]) if
# you're using some kind of DHCP. I would recommend a static IP setup, in which
# case leaving it empty still works but specifying will be more stable.
NODES = ['192.168.11.61']

# S_PORT and D_PORT are the ports used for the TCP and the UDP connection. If
# you don't know what to put in here, simple leave it alone. DO NOT use the
# same port for S_PORT and D_PORT, it won't work.
S_PORT = 5251
D_PORT = 5252

# LOGDIR specifies the directory which will hold your CSV logfiles and your
# SQLite databases. It will be created in /home/$USER or in /var/tmp if run as
# root. Their format can be specified by a timestamp. This way, you can decide
# how granular you want the loggings to be seperated. You can further add a
# string, for example the car name, seperated by underscore, to the file
# format. PLEASE DO NOT use spaces in the filenames. I haven't tested it and
# will therefore not make any promises as to how good it works, if at all.
# Additionally, the logfile will have the hostname of the system in their name.
# Please seperate subdirectories with '/'.
# Examples:
#LOGDIR = 'ConnectedRaceData/YYMMDD_PW6.15' # ConnectedRaceData/160114_PW6.15
#LOGDIR = 'CRD/MMM-YYYY_615' # CRD/Jan-2016_615
#LOGDIR = 'CRD/DDDD-HH_E-Wemding' # CRD/014-15_E-Wemding
# Scroll down for complete list of tokens.
# This can also be done via string composition:
PREFIX = 'ConnectedRaceData'
TIMESTAMP = 'YYYY-MM-DD'
SUFFIX = 'Werkstatt-Test'
# LOGDIR = PREFIX + '/' + TIMESTAMP + '_' + SUFFIX
LOGDIR = TIMESTAMP + '_' + SUFFIX

# CSV log file format works like the timestamps and the suffixes for LOGDIR. I
# recommend adding the CAN which was read. The name of the interface will be
# there, but might not be the same as the CAN read from the car.
# Additionally, the logfile will have the hostname of the system in their name.
# Here, have some examples:
#FILEFORMAT = 'YYYYMMDDD-PW6.15' # 20160114-PW6.15-$CAN_IFACE-$HOSTNAME.csv
#FILEFORMAT = 'PW6.15-YYMMDD' # PW6.15-160114-$CAN_IFACE-$HOSTNAME.csv
HOURSTAMP = 'HH-mm'
FILEFORMAT = HOURSTAMP + '_' + DEVICE + '_' + CAN_IFACE

###############################################################################
# Tokens
# Use the following tokens in formatting:
#
#                 Token   Output
# Year            YYYY    2000, 2001, 2002 ... 2012, 2013
#                 YY      00, 01, 02 ... 12, 13
# Month           MMMM    January, February, March ...
#                 MMM     Jan, Feb, Mar ...
#                 MM      01, 02, 03 ... 11, 12
#                 M       1, 2, 3 ... 11, 12
# Day of Year     DDDD    001, 002, 003 ... 364, 365
#                 DDD     1, 2, 3 ... 4, 5
# Day of Month    DD      01, 02, 03 ... 30, 31
#                 D       1, 2, 3 ... 30, 31
# Day of Week     dddd    Monday, Tuesday, Wednesday ...
#                 ddd     Mon, Tue, Wed ...
#                 d       1, 2, 3 ... 6, 7
# Hour            HH      00, 01, 02 ... 23, 24
#                 H       0, 1, 2 ... 23, 24
#                 hh      01, 02, 03 ... 11, 12
#                 h       1, 2, 3 ... 11, 12
# Minute          mm      00, 01, 02 ... 58, 59
#                 m       0, 1, 2 ... 58, 59
# Seperators      :, -    :, -
###############################################################################

# PROTOCOL specifies the messages used by the nodes to register with each
# other. It's in here mainly in case you want to create subnets of nodes.
PROTOCOL = [b'REG', b'ACK']
