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

@blueprint.route('', methods=['GET', 'POST'])
def index():
    """
    Retrieve a list of accounts or create a new account.
    
    Parameters:
    - None

    Returns:
    - Response Object
    """

    parameters = {key: flask.request.args[key] for key in flask.request.args if key in [
        'type',
        'size',
        'page'
    ]} if flask.request.method == 'GET' else {}
    make_response = finance.routes.response_maker(flask.url_for('accounts.index', **parameters))

    # Require the user to authenticate
    if 'id' not in flask.session:

        return make_response(data={
            'error': 'User is not logged in'
        }, headers={
            'WWW-Authenticate': 'Basic realm="Finance API"'
        }, status_code=401)
    
    # If this is a GET request, retrieve a list of accounts
    if flask.request.method == 'GET':

        # Begin building the query
        query, values = (
            "SELECT id, type, name, balance FROM accounts WHERE owner = %s"
        ), [
            flask.session['id']
        ]
    
        # Check for account type filter
        if 'type' in flask.request.args:

            account_type = flask.request.args.get('type', type=int)

            # Verify that it's an integer
            if account_type is None:

                return make_response(data={'error': 'Account type must be an integer'}, status_code=400)
            
            else:

                # Verify that it's a valid account type
                if account_type in account_types:

                    # Add the type filter to the query
                    query += " AND type = %s"
                    values.append(account_type)

                else:

                    return make_response(data={'error': 'Invalid account type'}, status_code=400)
        
        # Sort the results alphabetically
        query += " ORDER BY name ASC"

        page_size = 5

        # Check for page size
        if 'size' in flask.request.args:

            page_size = flask.request.args.get('size', type=int)

            # Verify that it's an integer
            if page_size is None:

                return make_response(data={'error': 'Page size must be an integer'}, status_code=400)
            
            else:

                # Verify that it's positive
                if page_size < 0:

                    return make_response(data={'error': 'Invalid page  size'}, status_code=400)
        
        page_number = 0

        # Check for page number
        if 'page' in flask.request.args:

            page_number = flask.request.args.get('page', type=int)

            # Verify that it's an integer
            if page_number is None:

                return make_response(data={'error': 'Page number must be an integer'}, status_code=400)
            
            else:

                # Verify that it's positive
                if page_number < 0:

                    return make_response(data={'error': 'Invalid page number'}, status_code=400)
        
        # Add the page filter to the query
        query += " LIMIT %s OFFSET %s"
        values.append(page_size)
        values.append(page_number * page_size)
        
        # Connect to the database
        db = finance.model.connect()

        # Search the database for accounts with the given filter
        accounts = db.execute(query + ";", values).fetchall()

        # Format each account before returning the response
        for account in accounts:

            # Include the account's URL in the response
            account['url'] = flask.url_for('accounts.detail', id=account['id'])
        
        # Adjust the parameters for the next page
        parameters['page'] = page_number + 1

        # Return the list of accounts with the URL for the next page
        return make_response(data={
            'accounts': accounts,
            'next': flask.url_for('accounts.index', **parameters)
        }, status_code=200)

    # If this is a POST request, create a new account
    elif flask.request.method == 'POST':
        
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

@blueprint.route('/<int:id>', methods=['GET', 'PUT', 'PATCH'])
def detail(id):
    """
    Show or update an existing account.
    
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

        # If this is a PUT/PATCH request, update the account details
        if flask.request.method in ['PUT', 'PATCH']:

            # Verify that JSON payload is present in the request
            if not flask.request.json:

                return make_response(data={'error': 'Request does not contain JSON payload'}, status_code=400)

            # Check for account type
            if 'type' in flask.request.json:

                account_type = flask.request.json['type']

                # Verify that it's an integer
                if isinstance(account_type, int):

                    # Verify that it's a valid account type
                    if account_type in account_types:

                        # Update the account type
                        account['type'] = account_type
                    
                    else:

                        return make_response(data={'error': 'Invalid account type'}, status_code=400)
                    
                else:

                    return make_response(data={'error': 'Account type must be an integer'})

            # Check for account name
            if 'name' in flask.request.json:

                account_name = flask.request.json['name']

                # Verify that it's a string
                if isinstance(account_name, str):

                    # And that it's the right length
                    if ((1 <= len(account_name)) and (len(account_name) <= 64)):

                        # Search for an account with the same name and owner
                        result = db.execute("SELECT COUNT(*) FROM accounts WHERE owner = %s AND name = %s AND NOT id = %s;", [
                            flask.session['id'],
                            account_name,
                            id
                        ]).fetchone()

                        # Verify that this isn't a duplicate account
                        if result['count'] != 0:

                            return make_response(data={'error': 'An account already exists with that name'}, status_code=409)
                        
                        else:

                            # Update the account name
                            account['name'] = account_name
                    
                    else:

                        return make_response(data={'error': 'Account name must be 1-64 characters'}, status_code=400)
                
                else:

                    return make_response(data={'error': 'Account name must be a string'}, status_code=400)

            # Update the account
            account = db.execute("UPDATE accounts SET type = %s, name = %s WHERE id = %s AND owner = %s RETURNING id, type, name, balance;", [
                account['type'],
                account['name'],
                id,
                flask.session['id']
            ]).fetchone()

        # Include the account's URL in the response
        account['url'] = flask.url_for('accounts.detail', id=id)

        # Return the account
        return make_response(data={'account': account}, status_code=200)

    else:

        return make_response(data={'error': 'Account not found'}, status_code=404)

finance.app.register_blueprint(blueprint)