try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'ConnectedRace is a bidirectional telemetry platform for vehicles.',
    'author': 'Florian Eich',
    'url': 'git.nrmncr.net/ConnectedRace',
    'download_url': 'git.nrmncr.net/ConnectedRace',
    'author_email': 'flrn@nrmncr.net',
    'version': '0.1',
    'install_requires': ['nose2','python-can','arrow'],
    'packages': ['connectedrace'],
    'scripts': [],
    'name': 'ConnectedRace'
}

setup(**config)
