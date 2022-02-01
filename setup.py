"""Finance package configuration."""

import setuptools

with open('README.md', 'r') as file:
    readme = file.read()

setuptools.setup(
    name='finance',
    author='Joe Zawisa',
    author_email='joe@joezawisa.com',
    description='Finance API',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/joezawisa/finance',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.10',
    install_requires=[
        'flask==2.0.2'
    ]
)