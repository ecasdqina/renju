from setuptools import find_packages, setup

setup(
    name='renju',
    version='0.1.1',
    entry_points={
        "console_scripts": [
            "renju=renju.main:main",
        ]
    },
    packages=find_packages(exclude=['tests', 'docs'])
)
