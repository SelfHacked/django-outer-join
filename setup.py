from setuptools import setup, find_packages

extra_test = [
    'pytest>=4',
    'pytest-runner>=4',
    'pytest-cov>=2',
    'pytest-django>=3',
    'psycopg2',
]
extra_dev = extra_test

extra_ci = extra_test + [
    'python-coveralls',
]

setup(
    name='django-outer-join',

    version='dev',

    python_requires='>=3.6',

    install_requires=[
        'Django>=2',
        'returns-decorator',
        'gimme_cached_property',
    ],

    extras_require={
        'test': extra_test,
        'dev': extra_dev,

        'ci': extra_ci,
    },

    packages=find_packages(),

    url='https://github.com/SelfHacked/django-outer-join',
    author='SelfHacked',
)
