# Finance API

by [Joe Zawisa](https://github.com/joezawisa)

## About

This project is a finance API to view transactions and balances of bank
accounts, investments, and other assets. The application is written in
[Python](https://www.python.org). It is built as a
[Docker](https://www.docker.com) image to run in a container.

## Code Structure

| Path                                                       | Description                                      |
| ---------------------------------------------------------- | ------------------------------------------------ |
| [`README.md`](README.md)                                   | Project documentation                            |
| [`.gitignore`](.gitignore)                                 | Git filter                                       |
| [`.dockerignore`](.dockerignore)                           | Docker filter                                    |
| [`Dockerfile`](Dockerfile)                                 | Docker build script                              |
| [`compose.yml`](compose.yml)                               | Docker configuration for development             |
| [`schema.sql`](schema.sql)                                 | Database schema                                  |
| [`requirements.txt`](requirements.txt)                     | Application dependencies                         |
| [`setup.py`](setup.py)                                     | Package configuration                            |
| [`finance/`](finance/)                                     | Application package                              |
| [`finance/__init__.py`](finance/__init__.py)               | Application initialization                       |
| [`finance/config.py`](finance/config.py)                   | Application configuration                        |
| [`finance/model.py`](finance/model.py)                     | Application database interface                   |
| [`finance/routes/`](finance/routes/)                       | API controllers                                  |
| [`finance/routes/index.py`](finance/routes/index.py)       | Index API controller                             |
| [`finance/routes/auth.py`](finance/routes.auth.py)         | Authentication API controller                    |
| [`finance/routes/users.py`](finance/routes/users.py)       | Users API controller                             |
| [`finance/routes/accounts.py`](finance/routes/accounts.py) | Accounts API controller                          |
| [`tools/`](tools/)                                         | Development tools                                |
| [`tools/requirements.txt`](tools/requirements.txt)         | Dependencies for local development environment   |
| [`tools/install`](tools/install)                           | Script to install local development environment  |
| [`tools/generateSecretKey`](tools/generateSecretKey)       | Script to generate a secret key for Flask        |
| [`tools/db`](tools/db)                                     | Script to manage the database                    |

## Database Structure

A [PostgreSQL](https://www.postgresql.org) database is required to run the
application. Its structure is defined in [`schema.sql`](schema.sql). The
[database management script](#manage-the-database) can be used to initialize and
perform other operations on the database.

### Users

The `users` table holds information about users of the application.

| Field      | Type          | Description                            |
| ---------- | ------------- | -------------------------------------- |
| `id`       | `BIGINT`      | A unique identifier for the user       |
| `email`    | `VARCHAR(64)` | The user's email address               |
| `name`     | `VARCHAR(64)` | The user's full name                   |
| `password` | `BYTEA`       | The user's password, salted and hashed |

### Accounts

The `accounts` table holds information about financial accounts.

| Field     | Type          | Description                         |
| --------- | ------------- | ----------------------------------- |
| `id`      | `BIGINT`      | A unique identifier for the account |
| `owner`   | `BIGINT`      | User to whom the account belongs    |
| `type`    | `SMALLINT`    | Account type                        |
| `name`    | `VARCHAR(64)` | Account name                        |
| `balance` | `REAL`        | Account balance                     |

### Transactions

The `transactions` table holds information about financial transactions.

| Field    | Type       | Description            |
| -------- | ---------- | ---------------------- |
| `id`     | `BIGINT`   | Transaction identifier |
| `type`   | `SMALLINT` | Transaction type       |
| `amount` | `REAL`     | Transaction amount     |
| `date`   | `DATE`     | Transaction date       |

### Transfers

The `transfers` table holds information about transfers between financial
accounts.

| Field    | Type     | Description                          |
| -------- | -------- | ------------------------------------ |
| `id`     | `BIGINT` | Transaction identifier               |
| `source` | `BIGINT` | Account transferred from             |
| `target` | `BIGINT` | Account transferred to               |

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

#### reset

The `reset` subcommand resets the database by dropping all the tables and then
reloading the [schema](schema.sql).

```bash
tools/db [options] reset
```

## API

The following endpoints are exposed by the finance API. When following the
examples, make sure to replace `localhost` with the hostname (or IP address) and
port of the server where you're hosting the application. You can also remove the
`-k` flag if you're not using a self-signed certificate.

### Index

Endpoint: `GET /`

Get a list of services available from the API.

#### Request Parameters

This endpoint does not require any parameters to process a request.

#### Response

This endpoint returns a list of API services. A status code of `200 OK`
indicates a successful response.

#### Example

```bash
curl -b cookies.txt -c cookies.txt -k -i -X GET 'https://localhost'
```
```json
{
    "services": {
        "index": "/",
        "login": "/login",
        "logout": "/logout",
        "users": "/users",
        "accounts": "/accounts",
        "types": {
            "accounts": "/accounts/types"
        }
    },
    "url": "/"
}
```

### Authentication

The authentication API provides method to login and logout as a registered user.

#### Login

Endpoint: `POST /login`

Login as a registered user.

##### Request Parameters

| Key        | Type   | Location | Description          | Required | Default |
| ---------- | ------ | -------- | -------------------- | -------- | ------- |
| `email`    | string | JSON     | User's email address | Yes      | None    |
| `password` | string | JSON     | User's password      | Yes      | None    |

##### Response

This endpoint does not return any data. It logs the user in by storing their
email address in a session cookie. A status code of `200 OK` indicates a
successful response.

##### Example

```bash
curl -b cookies.txt -c cookies.txt -k -i -X POST 'https://localhost/login' -H 'Content-Type: application/json' -d '{"email":"someone@example.com","password":"p4$5w0rd"}'
```
```json
{
    "url": "/login"
}
```

#### Logout

Endpoint: `POST /logout`

Logout from an active session.

##### Request Parameters

This endpoint does not require any parameters to process a request.

##### Response

This endpoint does not return any data. It logs the user out by clearing the
session cookie. A status code of `200 OK` indicates a successful response.

##### Example

```bash
curl -b cookies.txt -c cookies.txt -k -i -X POST 'https://localhost/logout'
```
```json
{
    "url": "/logout"
}
```

### Users

The users API is used to manage users of the application.

#### Create User

Endpoint: `POST /users`

Create a new user.

##### Request Parameters

| Key        | Type   | Location | Description          | Required | Default |
| ---------- | ------ | -------- | -------------------- | -------- | ------- |
| `name`     | string | JSON     | User's full name     | Yes      | None    |
| `email`    | string | JSON     | User's email address | Yes      | None    |
| `password` | string | JSON     | User's password      | Yes      | None    |

`name` must be 1-64 characters long.

`email` must be 1-64 characters long and a valid email address.

`password` must be 8-72 characters long.

##### Response

This endpoint returns the newly created user. It also logs the user in by
storing their email address in a session cookie. A status code of `201 Created`
indicates a successful response.

##### Example

```bash
curl -b cookies.txt -c cookies.txt -k -i -X POST 'https://localhost/users' -H 'Content-Type: application/json' -d '{"name":"John Doe","email":"someone@example.com","password":"p4$5w0rd"}'
```
```json
{
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "someone@example.com",
        "url": "/users/1"
    },
    "url": "/users"
}
```

#### Show User

Endpoints: `GET /users/<id>`

Get a user's profile.

##### Request Parameters

| Key  | Type    | Location | Description     | Required | Default |
| ---- | ------- | -------- | --------------- | -------- | ------- |
| `id` | integer | Path     | User identifier | Yes      | None    |

`id` must be a valid user identifier. If `self` is supplied in place of the `id` parameter, `id` is assumed to be the
identifier of the logged-in user.

##### Response

This endpoint returns the requested user's profile. A status code of `200 OK`
indicates a successful response.

##### Example

```bash
curl -b cookies.txt -c cookies.txt -k -i -X GET 'https://localhost/users/1'
```
```json
{
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "someone@example.com",
        "url": "/users/1"
    },
    "url": "/users/1"
}
```

### Accounts

The accounts API is used to manage financial accounts.

#### Show Account Types

Endpoint: `GET /accounts/types`

Get a list of account types.

##### Request Parameters

This endpoint does not require any parameters to process a request.

##### Response

This endpoint returns a list of account types. A status code of `200 OK`
indicates a successful response.

##### Example

```bash
curl -b cookies.txt -c cookies.txt -k -i -X GET 'https://localhost/accounts/types'
```
```json
{
    "types": [
        {
            "id": 0,
            "name": "Checking"
        },
        {
            "id": 1,
            "name": "Savings"
        }
    ],
    "url": "/accounts/types"
}
```

#### Create Account

Endpoint: `POST /accounts`

Create a new account.

##### Request Parameters

| Key        | Type    | Location | Description       | Required | Default |
| ---------- | ------- | -------- | ----------------- | -------- | ------- |
| `type`     | integer | JSON     | Account type      | Yes      | None    |
| `name`     | string  | JSON     | Account name      | Yes      | None    |
| `balance`  | decimal | JSON     | Beginning balance | No       | `0`     |

`type` must be a valid account type.

`name` must be 1-64 characters long.

##### Response

This endpoint returns the newly created account. A status code of `201 Created`
indicates a successful response.

##### Example

```bash
curl -b cookies.txt -c cookies.txt -k -i -X POST 'https://localhost/accounts' -H 'Content-Type: application/json' -d '{"type":0,"name":"My First Bank Account","balance":1.23}'
```
```json
{
    "account": {
        "id": 1,
        "type": 0,
        "name": "My First Bank Account",
        "balance": 1.23
    },
    "url": "/accounts"
}
```