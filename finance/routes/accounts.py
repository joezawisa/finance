"""Accounts API controller."""

import finance
import flask

blueprint = flask.Blueprint('accounts', __name__, url_prefix='/accounts')

finance.app.register_blueprint(blueprint)