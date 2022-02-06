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

@blueprint.route('', methods=['POST'])
def index():
    """
    Create a new account.
    
    Parameters:
    - None

    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('accounts.index'))

    # Require the user to authenticate
    if 'id' not in flask.session:

        return make_response(data={
            'error': 'User is not logged in'
        }, headers={
            'WWW-Authenticate': 'Basic realm="Finance API"'
        }, status_code=401)
    
    # Verify that JSON payload is present in the request
    if not flask.request.json:

        return make_response(data={'Request does not contain JSON payload'}, status_code=400)

    # Verify that account type is present in JSON payload
    if 'type' in flask.request.json:

        # And that it's an integer in the right range
        if not (isinstance(flask.request.json['type'], int) and (0 <= flask.request.json['type']) and (flask.request.json['type'] < len(account_types))):

            return make_response(data={
                'error': 'Account type must be an integer between 0 and %s' % (len(account_types) - 1)
            }, status_code=400)

    else:

        return make_response(data={'error': 'Missing account type'}, status_code=400)
    
    # Verify that account name is present in JSON payload
    if 'name' in flask.request.json:

        # And that it's a string with the right length
        if isinstance(flask.request.json['name'], str) and (1 <= len(flask.request.json['name'])) and (len(flask.request.json['name']) <= 64):

            # Connect to the database
            db = finance.model.connect()

            # Search for an account with the same name and owner
            result = db.execute("SELECT COUNT(*) FROM accounts WHERE owner = %s AND name = %s;", [
                flask.session['id'],
                flask.request.json['name']
            ]).fetchone()

            # Verify that this isn't a duplicate account
            if result['count'] != 0:

                return make_response(data={'error': 'An account already exists with that name'}, status_code=409)
        
        else:

            return make_response(data={'error': 'Account name must be a string containing 1-64 characters'}, status_code=400)

    else:

        return make_response(data={'error': 'Missing account name'}, status_code=400)
    
    # Check if account balance is present in JSON payload
    if 'balance' in flask.request.json:

        # Verify that it's a number
        if not (isinstance(flask.request.json['balance'], float) or isinstance(flask.request.json['balance'], int)):

            return make_response(data={'error': 'Account balance must be a number'}, status_code=400)

    # Connect to the database
    db = finance.model.connect()

    # Create the account
    account = db.execute("INSERT INTO accounts (owner, type, name, balance) VALUES (%s, %s, %s, %s) RETURNING id, type, name, balance;", [
        flask.session['id'],
        flask.request.json['type'],
        flask.request.json['name'],
        flask.request.json['balance']
    ]).fetchone() if 'balance' in flask.request.json else db.execute("INSERT INTO accounts (owner, type, name) VALUES (%s, %s, %s) RETURNING id, type, name, balance;", [
        flask.session['id'],
        flask.request.json['type'],
        flask.request.json['name']
    ]).fetchone()

    # Include the account's URL in the response
    account['url'] = flask.url_for('accounts.detail', id=account['id'])

    # Return the account
    return make_response(data={'account': account}, status_code=201)

@blueprint.route('/<int:id>', methods=['GET'])
def detail(id):
    """
    Show an existing account.
    
    Parameters:
    - None

    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('accounts.detail', id=id))

    # Require the user to authenticate
    if 'id' not in flask.session:

        return make_response(data={
            'error': 'User is not logged in'
        }, headers={
            'WWW-Authenticate': 'Basic realm="Finance API"'
        }, status_code=401)
    
    # Connect to the database
    db = finance.model.connect()

    # Search for an account with the specified ID owned by the logged-in user
    account = db.execute("SELECT id, type, name, balance FROM accounts WHERE id = %s AND owner = %s;", [
        id,
        flask.session['id']
    ]).fetchone()

    # Make sure the account exists
    if account:

        # Include the account's URL in the response
        account['url'] = flask.url_for('accounts.detail', id=id)

        # Return the account
        return make_response(data={'account': account}, status_code=200)

    else:

        return make_response(data={'error': 'Account not found'}, status_code=404)

finance.app.register_blueprint(blueprint)