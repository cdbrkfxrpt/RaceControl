import can
import logger
import antenna
import cable
import sys
import signal

def main():
    cabled = cable.CableDaemon()
    antennad = antenna.AntennaDaemon()
    loggingd = logger.LoggingDaemon()

    cabled.add_listener(antennad.cannon.buffer)
    antennad.add_listener(cabled.buffer)

    for listener in loggingd.loggers():
        cabled.add_listener(listener)
        antennad.add_listener(listener)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('\nExiting ConnectedRace.')
        sys.exit(0)

if __name__ == "__main__":
    main()
