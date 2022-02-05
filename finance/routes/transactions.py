"""Transactions API controller"""

import finance
import flask

blueprint = flask.Blueprint('transactions', __name__, url_prefix='/transactions')

finance.app.register_blueprint(blueprint)