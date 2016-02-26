import pytest
from connectedrace.globals import *
from connectedrace.antenna import *
from connectedrace.cannon import *
from connectedrace.bucket import *

@pytest.fixture(scope="session")
def message():
    return can.Message(data=[1,2,3,4,5,6,7,8])

@pytest.fixture(scope="session")
def node(message):
    return Node('127.0.0.1', message)

@pytest.fixture(scope="session")
def listener():
    return can.BufferedReader()

@pytest.fixture(scope="session")
def antenna(listener):
    return AntennaDaemon(listeners=[listener], node_ips=[])

@pytest.fixture(scope="session")
def cannon(antenna):
    return Cannon(antenna)

@pytest.fixture(scope="session")
def bucket_handler():
    return BucketHandler()

@pytest.fixture(scope="session")
def bucket(antenna):
    return Bucket(('', D_PORT), BucketHandler, antenna)
