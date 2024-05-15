from setuptools import setup, find_packages
import os

# Read requirements from the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

APP = ['main.py']  # Use debug_main.py as the main entry point
DATA_FILES = []
OPTIONS = {
    'iconfile': 'assets/logo.icns',
    'includes': ['Babel', 'pillow', 'charset_normalizer'] + [pkg.split('==')[0] for pkg in requirements],
    'excludes': ['PyInstaller'],
    'plist': {
        'CFBundleName': 'Excelerate',
        'CFBundleDisplayName': 'Excelerate',
        'CFBundleIdentifier': 'calumsiemer.dev.excelerate',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=requirements,
    packages=find_packages(),
)