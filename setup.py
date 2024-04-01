import os
from setuptools import setup, find_packages

requirements = [
    'Click', 'PyYAML', 'GitPython', 'giturlparse.py', 'virtualenv', 'requirements-parser', 'jinja2', 'psutil',
    'tabulate'
]

if not os.sys.platform.startswith('darwin'):
    requirements.append('pystemd')
    requirements.append('cryptography==2.3')

setup(
    name='qbe',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'qbe = qbe.bin:entry'
        ],
    },
)
