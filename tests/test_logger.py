import pytest
from connectedrace.logger import *

class TestLogging:
    def test_init(self, logger):
        pass

    def test_loggers(self, logger):
        assert logger.csv_logger in logger.loggers()
        assert logger.sqlite_logger in logger.loggers()
