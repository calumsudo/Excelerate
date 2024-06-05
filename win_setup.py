from setuptools import setup, find_packages, Command
import os

# Read requirements from the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Create a requirements list suitable for PyInstaller
includes = ['Babel', 'pillow', 'charset_normalizer'] + [pkg.split('==')[0] for pkg in requirements]

# PyInstaller options
OPTIONS = {
    'icon': 'assets/logo.ico',  # Use a .ico file for Windows
    'includes': includes,
    'excludes': ['PyInstaller'],
}

# Entry point for the application
entry_point = 'main.py'  # Ensure this is the correct entry point script

# Create a command class to integrate PyInstaller with setuptools
class BuildExeCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import PyInstaller.__main__
        PyInstaller.__main__.run([
            '--onefile',  # Create a single executable file
            '--windowed',  # Use this for GUI applications
            '--icon=' + OPTIONS['icon'],
            '--name=Excelerate',
            entry_point,
        ] + ['--hidden-import=' + inc for inc in OPTIONS['includes']]
        )

setup(
    name='Excelerate',
    version='0.1.0',
    description='Excelerate Application',
    author='Calum Siemer',
    packages=find_packages(),
    install_requires=requirements,
    cmdclass={
        'build_exe': BuildExeCommand,
    },
)
