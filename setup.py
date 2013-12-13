#!/usr/bin/env python

#from distutils.core import setup, Command
from setuptools import setup
from skos import __version__
'''
class TestCommand(Command):
    """
    Custom distutils command for running the test suite
    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os.path
        from test import unittest

        test_dir = os.path.join(os.path.dirname(__file__), 'test')
        package_suite = unittest.TestLoader().discover(test_dir)
        unittest.TextTestRunner(verbosity=2).run(package_suite)
'''
setup(name='python-skos',
      version=__version__,
      description='A basic implementation of some core elements of the SKOS object model',
      author='Jaimie Murdock',
      author_email='hrz@geodata.soton.ac.uk',
      url='http://github.com/inpho/python-skos',
      license='BSD',
      py_modules=['skos'],
  #    cmdclass = { 'test': TestCommand },
      install_requires =["RDFLib==2.4.2", "SQLAlchemy>=0.7.5", "iso8601plus"]
     )
