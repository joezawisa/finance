"""Users API controller"""

import finance
import flask

blueprint = flask.Blueprint('users', __name__, url_prefix='/users')

finance.app.register_blueprint(blueprint)