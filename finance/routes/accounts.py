"""Accounts API controller."""

import finance
import flask

account_types = {
    0: "Checking",
    1: "Savings"
}

blueprint = flask.Blueprint('accounts', __name__, url_prefix='/accounts')

@blueprint.route('/types', methods=['GET'])
def types():
    """
    Get a list of account types.
    
    Parameters:
    - None
    
    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('accounts.types'))

    # Return the list of account types
    return make_response(data={
        'types': sorted([{'id': t, 'name': account_types[t]} for t in account_types], key=lambda t: t['name'])
    }, status_code=200)

finance.app.register_blueprint(blueprint)