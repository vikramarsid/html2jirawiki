# coding=utf-8
"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from io import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='html2jirawiki',
    version='1.0.0',
    description='A sample Python project to convert HTML to JIRA Wiki',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vikramarsid/html2jirawiki',
    author='Vikram Arsid',
    author_email='vikramarsid@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],

    keywords='HTML, JIRA Wiki',  # Optional
    packages=find_packages(exclude=['docs', 'tests']),
    zip_safe=False,
    include_package_data=True,
    install_requires=['beautifulsoup4', 'six'],

)
