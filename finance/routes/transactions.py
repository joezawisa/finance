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

@blueprint.route('', methods=['GET', 'POST'])
def index():
    """
    Retrieve a list of transactions or create a new transaction.
    
    Parameters:
    - None
    
    Returns:
    - Response Object
    """

    parameters = {key: flask.request.args[key] for key in flask.request.args if key in [
        'type',
        'date',
        'account',
        'size',
        'page'
    ]} if flask.request.method == 'GET' else {}
    make_response = finance.routes.response_maker(flask.url_for('transactions.index', **parameters))

    # Require the user to authenticate
    if 'id' not in flask.session:

        return make_response(data={
            'error': 'User is not logged in'
        }, headers={
            'WWW-Authenticate': 'Basic realm="Finance API"'
        }, status_code=401)
    
    # If this is a GET request, retrieve a list of transactions
    if flask.request.method == 'GET':

        # Begin building the query
        query, values = (
            "SELECT id, type, amount, date FROM transactions WHERE ("
            "(SELECT owner FROM accounts WHERE accounts.id = (SELECT source FROM transfers WHERE transfers.id = transactions.id)) = %s OR "
            "(SELECT owner FROM accounts WHERE accounts.id = (SELECT target FROM transfers WHERE transfers.id = transactions.id)) = %s OR "
            "(SELECT owner FROM accounts WHERE accounts.id = (SELECT account FROM interest WHERE interest.id = transactions.id)) = %s)"
        ), [
            flask.session['id'],
            flask.session['id'],
            flask.session['id']
        ]
        
        # Check for transaction type filter
        if 'type' in flask.request.args:

            transaction_type = flask.request.args.get('type', type=int)

            # Verify that it's an integer
            if transaction_type is None:

                return make_response(data={'error': 'Transaction type must be an integer'}, status_code=400)

            else:

                # Verify that it's a valid transaction type
                if transaction_type in transaction_types:

                    # Add the type filter to the query
                    query += " AND type = %s"
                    values.append(transaction_type)
                
                else:

                    return make_response(data={'error': 'Invalid transaction type'}, status_code=400)
        
        # Check for transaction date filter
        if 'date' in flask.request.args:

            transaction_date = flask.request.args.get('date', type=str)

            # Verify that it's a string
            if transaction_date is None:

                return make_response(data={'error': 'Transaction date must be a string'}, status_code=400)
            
            else:

                try:

                    # Convert it to a date object
                    transaction_date = datetime.datetime.strptime(transaction_date, f'%Y-%m-%d')

                    # Add the date filter to the query
                    query += " AND date = %s"
                    values.append(transaction_date)

                except ValueError:

                    return make_response(data={'error': 'Transaction date must be formatted as YYYY-MM-DD'}, status_code=400)
        
        # Check for account ID filter
        if 'account' in flask.request.args:

            account_id = flask.request.args.get('account', type=int)

            # Verify that it's an integer
            if account_id is None:

                return make_response(data={'error': 'Account ID must be an integer'}, status_code=400)
            
            else:

                # Add the account ID filter to the query
                query += (
                    " AND ((SELECT source FROM transfers WHERE transfers.id = transactions.id) = %s "
                    " OR (SELECT target FROM transfers WHERE transfers.id = transactions.id) = %s"
                    " OR (SELECT account FROM interest WHERE interest.id = transactions.id) = %s)"
                )
                values.extend([
                    account_id,
                    account_id,
                    account_id
                ])

        # Sort the results by date and transaction ID
        query += " ORDER BY date DESC, id DESC"

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

                    return make_response(data={'error': 'Invalid page size'}, status_code=400)
        
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

        # Search the database for transactions with the given filter
        transactions = db.execute(query + ";", values).fetchall()

        # For each transaction, fetch the data relevant to the specific transaction type
        for transaction in transactions:

            # Check if this is a transfer
            if transaction['type'] == 0:

                # Get transfer fields from database
                transfer = db.execute("SELECT source, target FROM transfers WHERE transfers.id = %s;", [
                    transaction['id']
                ]).fetchone()

                # Make sure the transfer was found
                if transfer:

                    # Update the transaction with transfer fields
                    transaction.update(transfer)
                
                else:

                    return make_response(data={'error': 'Failed to retrieve transactions'}, status_code=500)
            
            # Check if this is an interest transaction
            elif transaction['type'] == 1:

                # Get interest fields from database
                interest = db.execute("SELECT account, startdate, enddate FROM interest WHERE interest.id = %s;", [
                    transaction['id']
                ]).fetchone()

                # Make sure the interest entry was found
                if interest:

                    # Format the start and end dates
                    if interest['startdate'] and interest['enddate']:

                        interest.update({
                            'startdate': interest['startdate'].strftime(f'%Y-%m-%d'),
                            'enddate': interest['enddate'].strftime(f'%Y-%m-%d')
                        })

                    # Update the transaction with interest fields
                    transaction.update(interest)
                
                else:

                    return make_response(data={'error': 'Failed to retrieve transactions'}, status_code=500)
            
            else:

                return make_response(data={'error': 'Encountered invalid transaction type'}, status_code=500)
        
            # Format the date and include the transaction's URL in the response
            transaction.update({
                'date': transaction['date'].strftime(f'%Y-%m-%d'),
                'url': flask.url_for('transactions.detail', id=transaction['id'])
            })
        
        # Adjust the parameters for the next page
        parameters['page'] = page_number + 1
        
        # Return the list of transactions with the URL for the next page
        return make_response(data={
            'transactions': transactions,
            'next': flask.url_for('transactions.index', **parameters)
        }, status_code=200)
    
    # If this is a POST request, create a new transaction
    elif flask.request.method == 'POST':

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