"""Finance package initializer."""

import flask
import logging

# Create an application object
app = flask.Flask(__name__)

# Configure logging for Gunicorn
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)