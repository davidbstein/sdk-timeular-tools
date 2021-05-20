from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

_NAME = 'sdk-timeular-tools'

setup(
  name=_NAME,
  version='0.1',
  long_description=readme(),
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Environment :: MacOS X',
    'Programming Language :: Python :: 3.9',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],
  description='A python wrapper around the Timeular HTTP API, and some notebooks of questionable usefulness',
  url=f'http://github.com/davidbstein/{_NAME}',
  author='stein',
  author_email=f'{_NAME}-pypi@emailcatcher.xyz',
  license='MIT',
  packages=['timeular'],
  )
