"""Finance package initializer."""

import flask
import logging

# Create an application object
app = flask.Flask(__name__)

# Create a custom WSGI app to fix Flask's URL generation
class WSGI(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        if 'APPLICATION_ROOT' in app.config:
            environ['SCRIPT_NAME'] = app.config['APPLICATION_ROOT']
        return self.app(environ, start_response)
app.wsgi_app = WSGI(app.wsgi_app)

# Read settings from config module
app.config.from_object('finance.config')

# Configure logging for Gunicorn
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# Tell our application about its components
import finance.model
import finance.routes