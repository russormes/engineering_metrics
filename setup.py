from setuptools import setup

setup(
    name='engineeringmetrics',
    version='0.1',
    description='A package for generating engineering metrics',
    author='Russell Ormes',
    author_email='russell.ormes@karhoo.com',
    packages=['engineeringmetrics'],
    # external packages as dependencies
    install_requires=['jira', 'PyJWT', 'py-dateutil', 'numpy'],
)
