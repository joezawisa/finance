"""Finance database model."""

import finance
import flask
import psycopg

def connect():
    """
    Connect to the database. Database credentials are sourced from the
    application configuration.
    
    Parameters:
    - None

    Returns:
    - PostgreSQL database connection object
    """

    # Check whether a database connection exists in Flask's global context
    if 'db' not in flask.g:

        # If it does not exist, connect to the database
        flask.g.db = psycopg.connect(
            user=finance.app.config['DB_USER'],
            password=finance.app.config['DB_PASSWORD'],
            host=finance.app.config['DB_HOST'],
            port=finance.app.config['DB_PORT'],
            dbname=finance.app.config['DB_NAME'],
            row_factory=psycopg.rows.dict_row
        )

    return flask.g.db

@finance.app.teardown_appcontext
def close(error = None):
    """
    Commit any pending transactions and close the database connection.

    Parameters:
    - error: error, if detected
    
    Returns:
    - None
    """

    # Retrieve database connection, if any, from Flask's global context
    db = flask.g.pop('db', None)

    # Check whether we found a connection
    if db is not None:

        # If we found a connection, check whether it's open
        if not (db.closed):

            # Commit any changes unless there was an error
            if not flask.g.pop('exception', None):
                
                db.commit()
            
            # Close the connection
            db.close()