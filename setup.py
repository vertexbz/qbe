from setuptools import setup, find_packages

setup(
    name='qbe',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click', 'PyYAML', 'GitPython', 'pystemd', 'giturlparse.py', 'virtualenv', 'requirements-parser', 'jinja2',
        'ansible-playbook-runner', 'ansible==7.5', 'cryptography==2.3'
    ],
    entry_points={
        'console_scripts': [
            'qbe = qbe.bin:entry'
        ],
    },
)
