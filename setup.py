from setuptools import find_packages, setup

setup(
    name='renju',
    version='0.1.0',
    entry_points={
        "console_scripts": [
            "renju=renju.judge:main",
        ]
    },
    packages=find_packages(exclude=['tests', 'docs'])
)
