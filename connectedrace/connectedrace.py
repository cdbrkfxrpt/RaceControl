import can
import logger
import antenna
import cable
import sys
import signal
import time

def main():
    cabled = cable.CableDaemon()
    antennad = antenna.AntennaDaemon()
    loggingd = logger.LoggingDaemon()

    cabled.add_listener(antennad.cannon.buffer)
    antennad.add_listener(cabled.buffer)

    for listener in loggingd.loggers():
        cabled.add_listener(listener)
        antennad.add_listener(listener)

    timestamp = time.perf_counter()
    try:
        while True:
            if time.perf_counter() - timestamp > 1.0:
                print('ConnectedRace running.')
                timestamp = time.perf_counter()
    except KeyboardInterrupt:
        print('\nExiting ConnectedRace.')
        sys.exit(0)

if __name__ == "__main__":
    main()
