"""Finance application configuration."""

import os

# Root URI of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = os.environ['APPLICATION_ROOT']

# Secret key for encrypting cookies
SECRET_KEY = os.environ['FLASK_KEY']

# Database credentials
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
DB_PORT = os.environ['DB_PORT']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']