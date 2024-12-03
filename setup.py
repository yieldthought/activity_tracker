from setuptools import setup, find_packages
import os
from activity_tracker import __version__

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
