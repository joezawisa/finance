"""Users API controller"""

import finance
import flask
import bcrypt
import re

blueprint = flask.Blueprint('users', __name__, url_prefix='/users')

@blueprint.route('', methods=['POST'])
def index():
    """
    Create a new user.
    
    Parameters:
    - None
    
    Returns:
    - Response Object
    """

    make_response = finance.routes.response_maker(flask.url_for('users.index'))

    # If the user is already logged in, don't allow them to create another user
    if 'id' in flask.session:

        return make_response(data={'error': 'User is already logged in'}, status_code=403)

    # Verify that JSON payload is present in the request
    if not flask.request.json:

        return make_response(data={'Request does not contain JSON payload'}, status_code=400)

    # Verify that name is present in JSON payload
    if 'name' in flask.request.json:

        # And that it's a string with the right length
        if not (isinstance(flask.request.json['name'], str) and (1 <= len(flask.request.json['name'])) and (len(flask.request.json['name']) <= 64)):
            
            return make_response(data={'error': 'Name must be a string containing 1-64 characters'}, status_code=400)

    else:

        return make_response(data={'error': 'Missing name'}, status_code=400)

    # Verify that email address is present in JSON payload
    if 'email' in flask.request.json:

        # And that it's a string with the right length
        if isinstance(flask.request.json['email'], str) and (1 <= len(flask.request.json['email'])) and (len(flask.request.json['email']) <= 64):
            
            # And that it's a valid email address
            if re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', flask.request.json['email']):

                # Connect to the database
                db = finance.model.connect()

                # Search a user with this email address
                result = db.execute("SELECT COUNT(*) FROM users WHERE email = %s;", [
                    flask.request.json['email']
                ]).fetchone()
                 
                # Verify that the email address isn't already taken
                if result['count'] != 0:

                    return make_response(data={'error': 'A user already exists with that email address'}, status_code=409)

            else:
                
                return make_response(data={'error': 'Invalid email address'}, status_code=400)

        else:

            return make_response(data={'error': 'Email address must be a string containing 1-64 characters'}, status_code=400)

    else:

        return make_response(data={'error': 'Missing email address'}, status_code=400)
    
    # Verify that password is present in JSON payload
    if 'password' in flask.request.json:

        # And that it's a string with the right length
        if not (isinstance(flask.request.json['password'], str) and (8 <= len(flask.request.json['password'])) and (len(flask.request.json['password']) <= 72)):

            return make_response(data={'Password must be a string containing 8-72 characters'}, status_code=400)

    else:

        return make_response(data={'error': 'Missing password'}, status_code=400)

    # Generate a random salt
    salt = bcrypt.gensalt()
    # Hash the new user's password
    hash = bcrypt.hashpw(flask.request.json['password'].encode(), salt)

    # Connect to the database
    db = finance.model.connect()

    # Create the user
    user = db.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id, name, email;", [
        flask.request.json['name'],
        flask.request.json['email'],
        hash
    ]).fetchone()

    # Log the user in
    flask.session['id'] = user['id']

    # Return the user
    return make_response(data={'user': user}, status_code=201)

finance.app.register_blueprint(blueprint)