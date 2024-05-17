import os.path

from setuptools import setup, find_packages

setup(
    name='qbe',
    version='0.1.0',
    packages=['qbe', *['qbe.' + p for p in find_packages(where='.', exclude=['tests'])]],
    package_dir={
        'qbe': os.path.dirname(__file__)
    },
    install_requires=[
        'Click', 'jinja2', 'dc-schema', 'requests', 'pyaml', 'tabulate', 'psutil', 'typing_extensions', 'inotify_simple'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'qbe = qbe.bin:entry'
        ],
    }
)
