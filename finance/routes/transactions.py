"""Transactions API controller"""

import finance
import flask
import datetime

transaction_types = {
    0: "Transfer",
    1: "Interest"
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

            # And that it's positive if this is a transfer or interest
            if (flask.request.json['type'] in [0, 1]) and not (flask.request.json['amount'] > 0):

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

        # Format the date and include transaction's URL in response
        transaction.update({
            'date': transaction['date'].strftime(f'%Y-%m-%d'),
            'url': flask.url_for('transactions.detail', id=transaction['id'])
        })

        # Return the transaction
        return make_response(data={'transaction': transaction}, status_code=201)
    
    # Check if this is an interest transaction
    if flask.request.json['type'] == 1:

        startdate = None

        # Check whether start date is present in JSON payload
        if 'startdate' in flask.request.json:

            # Verify that it's a string
            if isinstance(flask.request.json['startdate'], str):

                try:

                    # Convert it to a date object
                    startdate = datetime.datetime.strptime(flask.request.json['startdate'], f'%Y-%m-%d')

                except ValueError:

                    return make_response(data={'error': 'Start date must be formatted as YYYY-MM-DD'}, status_code=400)

            else:

                return make_response(data={'Start date must be a string'}, status_code=400)
        
        enddate = None

        # Check whether end date is present in JSON payload
        if 'enddate' in flask.request.json:

            # Verify that end date was not included without start date
            if not startdate:

                return make_response(data={'error': 'Cannot include end date without start date'}, status_code=400)

            # Verify that it's a string
            if isinstance(flask.request.json['enddate'], str):

                try:

                    # Convert it to a date object
                    enddate = datetime.datetime.strptime(flask.request.json['enddate'], f'%Y-%m-%d')

                except ValueError:

                    return make_response(data={'error': 'End date must be formatted as YYYY-MM-DD'}, status_code=400)
                
            else:

                return make_response(data={'End date must be a string'}, status_code=400)
        
        else:

            # Verify that start date was not included without end date
            if startdate:

                return make_response(data={'error': 'Cannot include start date without end date'})

        # Connect to the database
        db = finance.model.connect()

        # Verify that account is present in JSON payload
        if 'account' in flask.request.json:

            # And that it's an integer
            if isinstance(flask.request.json['account'], int):

                # Search for the account
                account = db.execute('SELECT balance FROM accounts WHERE id = %s AND owner = %s;', [
                    flask.request.json['account'],
                    flask.session['id']
                ]).fetchone()

                # Verify that the account exists (and belongs to the user)
                if not account:

                    return make_response(data={'error': 'Account does not exist'}, status_code=400)

            else:

                return make_response(data={'error': 'Account must be an integer'}, status_code=400)

        else:

            return make_response(data={'error': 'Missing account'}, status_code=400)

        # Adjust the balance of the account
        db.execute("UPDATE accounts SET balance = %s WHERE id = %s;", [
            account['balance'] + flask.request.json['amount'],
            flask.request.json['account']
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

        # Create the interest entry
        interest = db.execute("INSERT INTO interest (id, account, startdate, enddate) VALUES (%s, %s, %s, %s) RETURNING account, startdate, enddate;", [
            transaction['id'],
            flask.request.json['account'],
            flask.request.json['startdate'],
            flask.request.json['enddate']
        ]).fetchone() if startdate and enddate else db.execute("INSERT INTO interest (id, account) VALUES (%s, %s) RETURNING account, startdate, enddate;", [
            transaction['id'],
            flask.request.json['account'],
        ]).fetchone()

        # Include interest fields in response
        transaction.update(interest)

        # Format the start and end dates
        if transaction['startdate'] and transaction['enddate']:

            transaction.update({
                'startdate': transaction['startdate'].strftime(f'%Y-%m-%d'),
                'enddate': transaction['enddate'].strftime(f'%Y-%m-%d')
            })

        # Format the date and include transaction's URL in response
        transaction.update({
            'date': transaction['date'].strftime(f'%Y-%m-%d'),
            'url': flask.url_for('transactions.detail', id=transaction['id'])
        })

        # Return the transaction
        return make_response(data={'transaction': transaction}, status_code=201)

@blueprint.route('/<int:id>', methods=['GET'])
def detail(id):
    """
    Show a transaction.
    
    Parameters:
    - None

    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('transactions.detail', id=id))

    # Require the user to authenticate
    if 'id' not in flask.session:

        return make_response(data={
            'error': 'User is not logged in'
        }, headers={
            'WWW-Authenticate': 'Basic realm="Finance API"'
        }, status_code=401)

    # Connect to the database
    db = finance.model.connect()

    # Search for a transaction with the specified ID
    transaction = db.execute(
        "SELECT id, type, amount, date FROM transactions WHERE transactions.id = %s;", [
        id
    ]).fetchone()

    # Make sure the transaction exists
    if transaction:

        # Check if this is a transfer
        if transaction['type'] == 0:

            # Search the database for a transfer with the specified ID and owned by the logged-in user
            transfer = db.execute("SELECT source, target FROM transfers WHERE id = %s "
            "AND (SELECT owner FROM accounts WHERE accounts.id = transfers.source) = %s "
            "AND (SELECT owner FROM accounts WHERE accounts.id = transfers.target) = %s;", [
                id,
                flask.session['id'],
                flask.session['id']
            ]).fetchone()

            # Make sure the transfer was found
            if transfer:

                # Include transfer fields in response
                transaction.update(transfer)

            else:

                return make_response(data={'error': 'Transaction not found'}, status_code=404)

        # Check if this is an interest transaction
        elif transaction['type'] == 1:

            # Search the database for an interest entry with the specified ID and owned by the logged-in user
            interest = db.execute("SELECT account, startdate, enddate FROM interest WHERE id = %s "
            "AND (SELECT owner FROM accounts WHERE accounts.id = interest.account) = %s;", [
                id,
                flask.session['id']
            ]).fetchone()

            # Make sure the interest entry was found
            if interest:

                # Include interest fields in response
                transaction.update(interest)

                # Format the start and end dates
                if transaction['startdate'] and transaction['enddate']:

                    transaction.update({
                        'startdate': transaction['startdate'].strftime(f'%Y-%m-%d'),
                        'enddate': transaction['enddate'].strftime(f'%Y-%m-%d')
                    })

            else:

                return make_response(data={'error': 'Transaction not found'}, status_code=404)
            
        else:

            return make_response(data={'error': 'Invalid transaction type'}, status_code=500)
        
        # Format the date and include transaction's URL in response
        transaction.update({
            'date': transaction['date'].strftime(f'%Y-%m-%d'),
            'url': flask.url_for('transactions.detail', id=transaction['id'])
        })

        # Return the transaction
        return make_response(data={'transaction': transaction}, status_code=200)

    else:

        return make_response(data={'error': 'Transaction not found'}, status_code=404)

finance.app.register_blueprint(blueprint)