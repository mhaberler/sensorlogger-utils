from setuptools import setup, find_packages

import decode

setup_options = dict(
    name = 'decode_ble',
    version = decode.__version__,
    packages = find_packages(),
    #scripts = ['blah'],
    entry_points = '''
                [console_scripts]
                decode_ble=decode.decode:main
                   '''
)


setup(**setup_options)

