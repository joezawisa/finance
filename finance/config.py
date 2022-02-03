"""Finance application configuration."""

import os

# Root URI of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = os.environ['APPLICATION_ROOT']

# Secret key for encrypting cookies
SECRET_KEY = os.environ['FLASK_KEY']