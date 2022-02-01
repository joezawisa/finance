# Finance API

by [Joe Zawisa](https://github.com/joezawisa)

## About

This project is a finance API to view transactions and balances of bank
accounts, investments, and other assets. The application is written in
[Python](https://www.python.org).

## Code Structure

| Path                                         | Description                                        |
| -------------------------------------------- | -------------------------------------------------- |
| [`README.md`](README.md)                     | Project documentation                              |
| [`.gitignore`](.gitignore)                   | Git filter                                         |
| [`requirements.txt`](requirements.txt)       | Application dependencies                           |
| [`setup.py`](setup.py)                       | Package configuration                              |
| [`finance/`](finance/)                       | Application package                                |
| [`finance/__init__.py`](finance/__init__.py) | Application initialization                         |
| [`tools/`](tools/)                           | Development tools                                  |
| [`tools/install`](tools/install)             | Script to install local development environment    |

## Setup

### Install a Local Development Environment

To install a local development environment, you will need
[Python 3](https://www.python.org). Run the
[install script](tools/install) to create a
[Python virtual environment](https://docs.python.org/3/tutorial/venv.html).

```bash
tools/install
```

Now run the activation script to activate the virtual environment.

```bash
source env/bin/activate
```

If you want, you can deactivate the virtual environment later.

```bash
deactivate
```