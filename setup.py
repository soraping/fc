#!usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author: caoping
@file:   setup.py
@time:   2021/03/01
@desc:
"""
from setuptools import setup, find_packages

VERSION = '0.0.1'

setup(
    name='fc',
    version=VERSION,
    description='fund search',
    long_description='fund search',
    classifiers=[],
    keywords='fund asynico click rich inquirer',
    author='caoshiping',
    author_email='soraping@163.com',
    url='https://github.com/soraping/fc',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'aiohttp',
        'inquirer',
        'click',
        'rich'
    ]
)