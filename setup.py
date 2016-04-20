try:
    from setuptools import setup
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    from distutils.core import setup

config = {
    'description':
        'RaceControl is a bidirectional CAN telemetry platform for vehicles.',
    'author': 'Florian Eich',
    'url': 'git.nrmncr.net/RaceControl',
    'download_url': 'git.nrmncr.net/RaceControl',
    'author_email': 'flrn@nrmncr.net',
    'version': '0.1',
    'install_requires': [
        'pytest',
        'python-can',
        'flask',
        'gevent',
        'canmatrix',
        'arrow'
    ],
    'packages': ['racecontrol'],
    'scripts': [
        'bin/racecontrol',
        'bin/vcan_start',
        'bin/slcan_start',
        'bin/racecontrol_modules_load'
    ],
    'data_files': ['etc/racecontrol.cfg'],
    'name': 'RaceControl'
}

setup(**config)
