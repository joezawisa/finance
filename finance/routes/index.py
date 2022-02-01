"""Index API controller."""

import finance
import flask

@finance.app.route('/', methods = ['GET'])
def index():
    """
    Get a list of API endpoints.

    Parameters:
    - None

    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('index'))

    return make_response(data={
        'services': {
            'index': flask.url_for('index'),
            'login': flask.url_for('login'),
            'logout': flask.url_for('logout'),
            'users': flask.url_for('users.index'),
            'types': {
                'accounts': flask.url_for('accounts.types')
            }
        },
        'url': flask.url_for('index')
    }, status_code=200)