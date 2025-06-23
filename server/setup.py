"""Setup script for the NFC Reader/Writer System - PC Server Component."""

from setuptools import setup, find_packages

# Read version from __init__.py
with open('__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.1.0'

# Read README.md for long description
with open('README.md', 'r') as f:
    long_description = f.read()

# Read requirements.txt for dependencies
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='nfc-reader-writer-server',
    version=version,
    description='PC Server component for NFC Reader/Writer System',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='NFC Reader/Writer Team',
    author_email='contact@example.com',
    url='https://github.com/organization/nfc-reader-writer-system',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'nfc-server=server.main:main',
        ],
    },
)
