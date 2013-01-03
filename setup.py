from distutils.core import setup

setup(
    name='python-BLICK',
    version='0.2.9',
    author='Michael McAuliffe, Bruce Hayes',
    author_email='michael.e.mcauliffe@gmail.com',
    packages=['blick', 'blick.test'],
    scripts=['bin/BlickAFile.py'],
    url='http://pypi.python.org/pypi/python-BLICK/',
    license='LICENSE.txt',
    description='Python implementation of BLICK (a phonotactic probability calculator for English)',
    long_description=open('README.txt').read(),
    install_requires=[],
)
