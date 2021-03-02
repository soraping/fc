#!usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author: caoping
@file:   setup.py
@time:   2021/03/01
@desc:
"""
from setuptools import setup, find_packages

VERSION = '0.1.6'

setup(
    name='fundgz',
    version=VERSION,
    description='fund search',
    long_description='fund search',
    keywords='fund asynico click rich inquirer',
    author='caoshiping',
    author_email='soraping@163.com',
    url='https://github.com/soraping/fc',
    license='MIT',
    packages=find_packages(exclude=["*.txt"]),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'aiohttp',
        'inquirer',
        'click',
        'rich'
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'fundgz = fundgz.main:main'
        ]
    }
)