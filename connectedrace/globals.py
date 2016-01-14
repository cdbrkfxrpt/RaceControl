# CAN_IFACE specifies the name of the socketcan interface. This will be
# something like 'slcan0' or 'can0', depending what technology you use.
# SerialCAN uses 'slcan0', 'slcan1' and so on; the Linux Kernel Module for
# MCP251x over SPI tends to use 'can0', 'can1' and so on. If you have more than
# one CAN interface you want to log, run several ConnectedRace instances (or
# contact me at florian.eich@gmail.com, chances are I will help you out.
# 'vcan0' is the Linux virtual CAN interface used for testing.
CAN_IFACE = 'vcan0'

# NODES specifies the IP addresses of your other nodes. Leave empty ([]) if
# you're using some kind of DHCP. I would recommend a static IP setup, in which
# case leaving it empty still works but specifying will be more stable.
NODES = ['192.168.10.2']

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
# A complete list of flags is at the end of this file.
# This can also be done via string composition:
PREFIX = 'ConnectedRaceData'
TIMESTAMP = 'YY-MMM-DD'
SUFFIX = 'PW7.16-Area'
LOGDIR = PREFIX + '/' + TIMESTAMP + '_' SUFFIX

# CSV log file format works like the timestamps and the suffixes for LOGDIR. I
# recommend adding the CAN which was read. The name of the interface will be
# there, but might not be the same as the CAN read from the car.
# Additionally, the logfile will have the hostname of the system in their name.
# Here, have some examples:
#FILEFORMAT = 'YYYYMMDDD-PW6.15' # 20160114-PW6.15-$CAN_IFACE-$HOSTNAME.csv
#FILEFORMAT = 'PW6.15-YYMMDD' # PW6.15-160114-$CAN_IFACE-$HOSTNAME.csv
FILEFORMAT = 'HH_CAN4-PW6.15'# 15_CAN4-PW6.15-$CAN_IFACE-$HOSTNAME.csv


# PROTOCOL specifies the messages used by the nodes to register with each
# other. It's in here mainly in case you want to create subnets of nodes.
PROTOCOL = [b'REG', b'ACK']
