#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.core import setup

for cmd in ('egg_info', 'develop'):
    import sys

    if cmd in sys.argv:
        from setuptools import setup

setup(
    name='django-paymaster',
    version='0.1.2',
    author='Dmitriy Vlasov',
    author_email='scailer@russia.ru',

    include_package_data=True,
    packages=['paymaster'],
    package_data={
        'paymaster': ['migrations/*.py', 'templates/paymaster/*.html']
    },

    url='https://github.com/scailer/django-paymaster/',
    license='MIT license',
    description='Application for integration PayMaster payment '
                'system in Django projects.',
    long_description='Приложение для интеграции платежной системы PayMaster '
                     '(http://paymaster.ru/) в проекты на Django. Реализовано '
                     'только основное API PayMaster, согласно спецификации'
                     'http://paymaster.ru/Partners/ru/docs/protocol/\n\n'
                     'С ознакомиться документацией, а так же сообщить об '
                     'ошибках можно на странице проекта '
                     'http://github.com/scailer/django-paymaster/',

    requires=['django (>= 1.5)', 'pytz', 'simple_crypt'],

    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    ),
)
