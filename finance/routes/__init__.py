"""Finance routes initializer."""

import finance
import flask

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