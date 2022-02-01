"""Finance routes initializer."""

import finance
import flask
import werkzeug.exceptions

# Simplify response construction in controllers
def response_maker(url):
    """
    Create a function to make a response from JSON data, headers, and status code.

    Parameters:
    - url: Default string to return in URL field of JSON data.

    Returns:
    - function(dict, dict, int) -> Response
    """

    def make_response(data = {}, headers = {}, status_code = None):
        """
        Make a response from data, headers, and status code.

        Parameters:
        - data: Response Data
        - headers: Response Headers
        - status_code: HTTP Status Code

        Returns:
        - Response Object
        """

        default = {'url': url}
        default.update(data)
        response = flask.jsonify(default)
        response.headers.extend(headers)

        if status_code:

            response.status_code = status_code

        return response
    
    return make_response

# Return JSON instead of HTML for HTTP errors
@finance.app.errorhandler(werkzeug.exceptions.HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # Let other functions know that there was an exception
    # (since they will no longer receive the exception object)
    flask.g.exception = e
    # Start with the correct headers and status code from the error
    response = e.get_response()
    # Replace the body with JSON
    response.data = flask.json.dumps({'error': e.description})
    response.content_type = 'application/json'
    return response

# Import API controllers
from . import index
from . import auth
from . import users