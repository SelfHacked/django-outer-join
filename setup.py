from setuptools import setup, find_packages

setup(
    name='django-outer-join',

    version='dev',

    python_requires='>=3.6',

    install_requires=[
        'Django>=1.11',
        'selfhacked-util @ https://github.com/SelfHacked/selfhacked-util/archive/master.zip',
    ],

    packages=find_packages(),

    url='https://github.com/SelfHacked/django-outer-join',
    author='SelfHacked',
)
