"""
This file is used to set up the project package.
"""

from setuptools import setup, find_packages

setup(
    name='consortium-blockchain',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask==2.0.1',
        'Werkzeug==2.0.3',
    ],
    entry_points={
        'console_scripts': [
            'consortium-blockchain=network:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A consortium blockchain application with membership management',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/consortium-blockchain',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
