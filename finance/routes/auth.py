"""Authentication API controller."""

import finance
import flask
import bcrypt
import re

@finance.app.route('/login', methods = ['POST'])
def login():
    """
    Login as a registered user.
    
    Parameters:
    - None
    
    Returns:
    - Response Object
    """

    make_reponse = finance.routes.response_maker(flask.url_for('login'))

    # If the user is already logged in, there's nothing to do
    if 'id' in flask.session:

        return make_reponse(data={'error': 'User is already logged in'}, status_code=403)

    # Verify that JSON payload is present in the request
    if not flask.request.json:

        return make_reponse(data={'error': 'Request does not contain JSON payload'}, status_code=400)

    # Verify that email address is present in JSON payload
    if 'email' in flask.request.json:

        # And that it's a string with the right length
        if isinstance(flask.request.json['email'], str) and (1 <= len(flask.request.json['email'])) and (len(flask.request.json['email']) <= 64):
        
            # And that it's a valid email address
            if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', flask.request.json['email']):
                
                return make_reponse(data={'error': 'Invalid email address'}, status_code=400)

        else:

            return make_reponse(data={
                'error': 'Invalid credentials'
            }, headers={
                'WWW-Authenticate': 'Basic realm="Finance API"'
            }, status_code=401)

    else:

        return make_reponse(data={'error': 'Missing email address'}, status_code=400)
    
    # Verify that password is present in JSON payload
    if 'password' in flask.request.json:

        # And that it's a string with the right length
        if not (isinstance(flask.request.json['password'], str) and (8 <= len(flask.request.json['password'])) and (len(flask.request.json['password']) <= 72)):

            return make_reponse(data={
                'error': 'Invalid credentials'
            }, headers={
                'WWW-Authenticate': 'Basic realm="Finance API"'
            }, status_code=401)

    else:

        return make_reponse(data={'error': 'Missing password'}, status_code=400)
    
    # Connect to the database
    db = finance.model.connect()

    # Search the database for the user and get their user ID and password
    user = db.execute("SELECT id, password FROM users WHERE email = %s;", [
        flask.request.json['email']
    ]).fetchone()

    # If the user was not found, reject the login request
    if user:

        # If the user was found, check their password
        if bcrypt.checkpw(flask.request.json['password'].encode(), bytes(user['password'])):

            # If their password was right, log them in
            flask.session['id'] = user['id']

            return make_reponse(status_code=200)

        else:

            # If their password was wrong, reject the login request
            return make_reponse(data={
                'error': 'Invalid credentials'
            }, headers={
                'WWW-Authenticate': 'Basic realm="Finance API"'
            }, status_code=401)

    else:
        
        return make_reponse(data={
            'error': 'Invalid credentials'
        }, headers={
            'WWW-Authenticate': 'Basic realm="Finance API"'
        }, status_code=401)

@finance.app.route('/logout', methods = ['POST'])
def logout():
    """
    Logout from an active session.
    
    Parameters:
    - None
    
    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('logout'))

    # If the user isn't logged in, there's nothing to do
    if 'id' not in flask.session:

        return make_response(data={
            'error': 'User is not logged in'
        }, headers={
            'WWW-Authenticate': 'Basic realm="Finance API"'
        }, status_code=401)
    
    # If the user is logged in, clear their session to log them out
    flask.session.clear()

    return make_response(status_code=200)