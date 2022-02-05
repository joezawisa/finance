"""Transactions API controller"""

import finance
import flask

transaction_types = {}

blueprint = flask.Blueprint('transactions', __name__, url_prefix='/transactions')

@blueprint.route('/types', methods=['GET'])
def types():
    """
    Get a list of transaction types.
    
    Parameters:
    - None
    
    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('transactions.types'))

    # Return the list of transaction types
    return make_response(data={
        'types': sorted([{'id': t, 'name': transaction_types[t]} for t in transaction_types], key=lambda t: t['name'])
    }, status_code=200)

finance.app.register_blueprint(blueprint)