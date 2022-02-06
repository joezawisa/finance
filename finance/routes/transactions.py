"""Transactions API controller"""

import finance
import flask
import datetime

transaction_types = {
    0: "Transfer"
}

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

@blueprint.route('', methods=['POST'])
def index():
    """
    Create a new transaction.
    
    Parameters:
    - None
    
    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('transactions.index'))

    # Require the user to authenticate
    if 'id' not in flask.session:

        return make_response(data={
            'error': 'User is not logged in'
        }, headers={
            'WWW-Authenticate': 'Basic realm="Finance API"'
        }, status_code=401)

    # Verify that JSON payload is present in the request
    if flask.request.json is None:

        return make_response(data={'error': 'Request does not contain JSON payload'}, status_code=400)
    
    # Verify that transaction type is present in JSON payload
    if 'type' in flask.request.json:

        # And that it's a number
        if isinstance(flask.request.json['type'], int):

            if flask.request.json['type'] not in transaction_types:

                return make_response(data={'error': 'Invalid transaction type'}, status_code=400)

        else:

            return make_response(data={'error': 'Transaction type must be a number'}, status_code=400)
    
    else:

        return make_response(data={'error': 'Missing transaction type'}, status_code=400)

    # Verify that transaction amount is present in JSON payload
    if 'amount' in flask.request.json:

        # And that it's a number
        if (isinstance(flask.request.json['amount'], float) or isinstance(flask.request.json['amount'], int)):

            # And that it's positive if this is a transfer
            if (flask.request.json['type'] in [0]) and not (flask.request.json['amount'] > 0):

                return make_response(data={'error': 'Transaction amount must be positive'}, status_code=400)
        
        else:

            return make_response(data={'error': 'Transaction amount must be a number'}, status_code=400)

    else:

        return make_response(data={'error': 'Missing transaction amount'}, status_code=400)

    date = None

    # Check whether transaction date is present in JSON payload
    if 'date' in flask.request.json:

        # Verify that it's a string
        if isinstance(flask.request.json['date'], str):

            try:

                # Convert it to a date object
                date = datetime.datetime.strptime(flask.request.json['date'], f'%Y-%m-%d')

            except ValueError:

                return make_response(data={'error': 'Transaction date must be formatted as YYYY-MM-DD'}, status_code=400)
            
        else:

            return make_response(data={'Transaction date must be a string'}, status_code=400)

    # Check if this is a transfer
    if flask.request.json['type'] == 0:

        source = None
        target = None

        # Connect to the database
        db = finance.model.connect()

        # Verify that transfer source is present in JSON payload
        if 'source' in flask.request.json:

            # And that it's an integer
            if isinstance(flask.request.json['source'], int):

                # Search for the transfer source account
                source = db.execute('SELECT balance FROM accounts WHERE id = %s AND owner = %s;', [
                    flask.request.json['source'],
                    flask.session['id']
                ]).fetchone()

                # Verify that the account exists (and belongs to the user)
                if not source:

                    return make_response(data={'error': 'Source account does not exist'}, status_code=400)

            else:

                return make_response(data={'error': 'Source account must be an integer'}, status_code=400)

        else:

            return make_response(data={'error': 'Missing source account'}, status_code=400)

        # Verify that transfer target is present in JSON payload
        if 'target' in flask.request.json:

            # And that it's an integer
            if isinstance(flask.request.json['target'], int):

                # Search for the transfer target account
                target = db.execute('SELECT balance FROM accounts WHERE id = %s AND owner = %s;', [
                    flask.request.json['target'],
                    flask.session['id']
                ]).fetchone()

                # Verify that the account exists (and belongs to the user)
                if target:

                    # Verify that the target account is not the same as the source account
                    if flask.request.json['target'] == flask.request.json['source']:

                        return make_response(data={'error': 'Target account cannot be same as source account'}, status_code=400)

                else:

                    return make_response(data={'error': 'Target account does not exist'}, status_code=400)

            else:

                return make_response(data={'error': 'Target account must be an integer'}, status_code=400)

        else:

            return make_response(data={'error': 'Missing target account'}, status_code=400)

        # Adjust the balance of the source account
        db.execute("UPDATE accounts SET balance = %s WHERE id = %s;", [
            source['balance'] - flask.request.json['amount'],
            flask.request.json['source']
        ])

        # Adjust the balance of the target account
        db.execute("UPDATE accounts SET balance = %s WHERE id = %s;", [
            target['balance'] + flask.request.json['amount'],
            flask.request.json['target']
        ])

        # Create the transaction
        transaction = db.execute("INSERT INTO transactions (type, amount, date) VALUES (%s, %s, %s) RETURNING id, type, amount, date;", [
            flask.request.json['type'],
            flask.request.json['amount'],
            date
        ]).fetchone() if 'date' in flask.request.json else db.execute("INSERT INTO transactions (type, amount) VALUES (%s, %s) RETURNING id, type, amount, date;", [
            flask.request.json['type'],
            flask.request.json['amount'],
        ]).fetchone()

        # Create the transfer
        transfer = db.execute("INSERT INTO transfers (id, source, target) VALUES (%s, %s, %s) RETURNING source, target;", [
            transaction['id'],
            flask.request.json['source'],
            flask.request.json['target']
        ]).fetchone()

        # Include transfer fields in response
        transaction.update(transfer)

        # Format the date
        transaction.update({
            'date': transaction['date'].strftime(f'%Y-%m-%d')
        })

        # Return the transaction
        return make_response(data={'transaction': transaction}, status_code=201)

finance.app.register_blueprint(blueprint)