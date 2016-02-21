from setuptools import setup, find_packages

import rosevrobank as meta


def long_description():
    with open('README.md') as f:
        rst = f.read()
        return rst

setup(
    name='django-rosevrobank',
    version=meta.__version__,
    description=meta.__doc__,
    author=meta.__author__,
    author_email=meta.__contact__,
    long_description=long_description(),
    url='https://github.com/nimoism/django-rosevrobank',
    platforms=["any"],
    packages=find_packages(),
    install_requires=[
        'django-extensions',
        'python-rosevrobank-api',
    ],
    dependency_links=[
        'git+https://github.com/nimoism/python-rosevrobank-api.git#egg=python-rosevrobank-api'
    ],
    scripts=[],
    classifiers=[
        'Development Status :: 2 - Pre-alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Framework :: Django',
    ]
)
