from setuptools import setup, find_packages
import os

# Read version from _version.py
with open('activity_tracker/_version.py', 'r') as f:
    exec(f.read())

setup(
    name="activity-tracker",
    version=__version__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'activity-tracker=activity_tracker.tracker:main',
        ],
    },
    install_requires=[
        'pynput>=1.7.0',
        'pyobjc-framework-Quartz>=10.0',
    ],
)
