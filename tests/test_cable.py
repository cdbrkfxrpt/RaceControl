import pytest
from connectedrace.cable import *

class TestCable:
    def test_init(self, cable):
        assert not cable.listeners

    def test_add_listener(self, cable, listener):
        cable.add_listener(listener)
        assert listener in cable.listeners
        cable.listeners = []
        assert not cable.listeners

    def test_run_notifier(self, cable):
        pass

    def test_stop_notifier(self, cable):
        pass

    def test_operate(self, cable):
        pass
