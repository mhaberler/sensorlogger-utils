from setuptools import setup, find_packages

import decode

setup_options = dict(
    name='decode_ble',
    version=decode.__version__,
    install_requires=[
        'Click', 'TheengsDecoder'
    ],
    entry_points='''
                [console_scripts]
                decode_ble=decode.decode:cli
                   '''
)


setup(**setup_options)
