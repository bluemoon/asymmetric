from setuptools import setup, find_packages
import os
import sys

VERSION = "0.5"
setup(
    name = "asymmetric",
    version = VERSION,
    packages = find_packages('src'),
    package_dir = {'':'src'},
    zip_safe=False,
    include_package_data=True,
    license='GPL',
    author='Alex Toney',
    author_email='toneyalex@gmail.com',
    test_suite="nose.collector",
    tests_require="nose",
)
