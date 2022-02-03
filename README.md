# Finance API

by [Joe Zawisa](https://github.com/joezawisa)

## About

This project is a finance API to view transactions and balances of bank
accounts, investments, and other assets. The application is written in
[Python](https://www.python.org). It is built as a
[Docker](https://www.docker.com) image to run in a container.

## Code Structure

| Path                                                 | Description                                      |
| ---------------------------------------------------- | ------------------------------------------------ |
| [`README.md`](README.md)                             | Project documentation                            |
| [`.gitignore`](.gitignore)                           | Git filter                                       |
| [`.dockerignore`](.dockerignore)                     | Docker filter                                    |
| [`Dockerfile`](Dockerfile)                           | Docker build script                              |
| [`compose.yml`](compose.yml)                         | Docker configuration for development             |
| [`schema.sql`](schema.sql)                           | Database schema                                  |
| [`requirements.txt`](requirements.txt)               | Application dependencies                         |
| [`setup.py`](setup.py)                               | Package configuration                            |
| [`finance/`](finance/)                               | Application package                              |
| [`finance/__init__.py`](finance/__init__.py)         | Application initialization                       |
| [`finance/config.py`](finance/config.py)             | Application configuration                        |
| [`finance/model.py`](finance/model.py)               | Application database interface                   |
| [`tools/`](tools/)                                   | Development tools                                |
| [`tools/requirements.txt`](tools/requirements.txt)   | Dependencies for local development environment   |
| [`tools/install`](tools/install)                     | Script to install local development environment  |
| [`tools/generateSecretKey`](tools/generateSecretKey) | Script to generate a secret key for Flask        |
| [`tools/db`](tools/db)                               | Script to manage the database                    |

## Database Structure

A [PostgreSQL](https://www.postgresql.org) database is required to run the
application. Its structure is defined in [`schema.sql`](schema.sql). The
[database management script](#manage-the-database) can be used to initialize and
perform other operations on the database.

## Setup

### Install a Local Development Environment

To install a local development environment, you will need
[Python 3](https://www.python.org). Run the
[install script](tools/install) to create a
[Python virtual environment](https://docs.python.org/3/tutorial/venv.html). For
the install script to work correctly, you will also need
[OpenSSL](https://www.openssl.org) installed because the script uses it to
create SSL/TLS credentials.

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

You can make changes and run the application in the development environment on
your local machine, but it's quicker, easier, and more like what will happen in
production if you use Docker instead.

## Build the Application

You will need to have [Docker](https://www.docker.com) installed to build and
run the application.

Our [`Dockerfile`](Dockerfile) tells [Docker](https://www.docker.com) how to
build the application image. The easiest way to build the application is with
[Docker Compose](https://docs.docker.com/compose/).

```bash
docker compose build
```

Alternatively, you can use the
[`docker build`](https://docs.docker.com/engine/reference/commandline/build/)
command.

### Build Arguments

These arguments must be present to build the application. If building with
[Docker Compose](https://docs.docker.com/compose/), [`compose.yml`](compose.yml)
will set them for you.

| Name | Description                                                                                          | Required | Default   |
| ---- | ---------------------------------------------------------------------------------------------------- | -------- | --------- |
| `TZ` | Time zone (see [Wikipedia](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for format) | No       | `Etc/UTC` |

## Run the Application

Our [`compose.yml`](compose.yml) tells [Docker](https://www.docker.com) how to
run the application. This is handy for development because we can run the
application in a container the same way it will be run in production. To run the
application, use [Docker Compose](https://docs.docker.com/compose/).

```bash
docker compose up
```

To run the application in detached mode (in the background), use the `-d` flag.

```bash
docker compose up -d
```

If you've made any changes to the [`Dockerfile`](Dockerfile), you'll need to let
[Docker Compose](https://docs.docker.com/compose/) know that it should rebuild
the application image before starting the container again. You can do so by
passing the `--build` flag to the same command.

```bash
docker compose up --build
```

```bash
docker compose up -d --build
```

Once the application is running, you can stop it either by pressing `Ctl`-`C`.
You can also stop it via the
[Docker Dashboard](https://docs.docker.com/desktop/dashboard/) or with
[Docker Compose](https://docs.docker.com/compose/).

```bash
docker compose stop
```

After stopping the application, it is often helpful to remove its containers.
This ensures a fresh start next time you run the application.

```bash
docker compose down
```

### Database

A [PostgreSQL](https://www.postgresql.org) database is required to run the
application. If running with [Docker Compose](https://docs.docker.com/compose/),
[`compose.yml`](compose.yml) will automatically bring up a
[PostgreSQL](https://www.postgresql.org) database for you. Connection details
are supplied to the application with
[environment variables](#environment-variables).

### Environment Variables

These environment variables must be present to run the application. If running
with [Docker Compose](https://docs.docker.com/compose/),
[`compose.yml`](compose.yml) will set them for you.

| Name               | Description                                       | Required | Default |
| ------------------ | ------------------------------------------------- | -------- | ------- |
| `APPLICATION_ROOT` | Root URI of the application                       | No       | `/`     |
| `FLASK_KEY`        | Secret key for encrypting Flask's session cookies | Yes      | None    |
| `DB_HOST`          | Database server hostname/IP address               | Yes      | None    |
| `DB_PORT`          | Database server TCP port                          | No       | `5432`  |
| `DB_NAME`          | Databse name                                      | Yes      | None    |
| `DB_USER`          | Database user                                     | Yes      | None    |
| `DB_PASSWORD`      | Database password                                 | Yes      | None    |

You can also set the `TZ` environment variable when you run the application to
configure the time zone. However, it is better to set the time zone when
building the application.

## Development Tools

The [`tools`](tools/) directory contains development tools and is not built into
the application image.

### Install

The [install script](tools/install) installs a local development environment.

```bash
tools/install
```

See [Install a Local Development Environment](#install-a-local-development-environment)
for details.

### Generate Secret Key

The [secret key generator](tools/generateSecretKey) generates a secret key that
can be used to encrypt [Flask](https://flask.palletsprojects.com)'s session
cookies.

```bash
tools/generateSecretKey
```

To use the secret key that this script generates, pass it to
[Flask](https://flask.palletsprojects.com) in the `FLASK_KEY` environment
variable.

### Manage the Database

The [database management script](tools/db) makes it easy to perform operations
on a PostgreSQL database. Each command to manage the database starts with
`tools/db` followed by several options.

| Short | Long         | Description                | Required | Default     |
| ----- | ------------ | -------------------------- | -------- | ----------- |
| `-u`  | `--user`     | Database user              | No       | `finance`   |
| `-p`  | `--password` | Database password          | No       | `finance`   |
| `-h`  | `--host`     | Server hostname/IP address | No       | `localhost` |
| `-t`  | `--port`     | Server TCP port            | No       | `5432`      |
| `-d`  | `--database` | Database name              | No       | `finance`   |

The operation to perform is specified by a subcommand.

```bash
tools/db [options] <subcommand>
```

If we wanted to explicitly specify all of the connection options, our command
would look something like this.

```bash
tools/db -u <user> -p <password> -h <host> -t <port> -d <database> <subcommand>
```

#### init

The `init` subcommand initializes the database by loading it from the
[`schema`](schema.sql).

```bash
tools/db [options] init
```