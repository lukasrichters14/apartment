import flask
from flask import request, jsonify, make_response
from flask_cors import CORS

import sqlite3

from random import randint
import time

import jwt

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

app = flask.Flask(__name__)
app.config['DEBUG'] = True

# Prevent CORS errors.
CORS(app)

USERS_DB = './data/users.db'
PUBLIC_KEY_FILE_NAME = './keys/public-key.pem'
PRIVATE_KEY_FILE_NAME = './keys/private-key.pem'

# Get private key.
with open(PRIVATE_KEY_FILE_NAME, "rb") as key_file:
    PRIVATE_KEY = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

# Get public key.
with open(PUBLIC_KEY_FILE_NAME, "rb") as key_file:
    PUBLIC_KEY = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )


def create_dict(cursor, row):
    """
    Specifies how to create a dictionary using the row_factory function.
    :param cursor: [cursor] the entry point for the database.
    :param row: [int] the current row.
    :return: [dict] the dictionary created by the row_factory.
    """

    d = {}
    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]
    return d


def query_db(db, query):
    """
    Performs an SQL query on a database.
    :param db: [string] the file path to the database.
    :param query: [string] an SQL-formatted query to the database.
    :return: [list] the SQL response from the query.
    """
    # Connect to the database.
    database = sqlite3.connect(db)
    # Set the format of the return of the SQL query.
    database.row_factory = create_dict
    cursor = database.cursor()
    result = cursor.execute(query).fetchall()
    cursor.close()
    return result


def modify_db(db, query):
    """
    Modifies the given database according to the given command.
    :param db: [string] the database to modify.
    :param query: [string] the SQL command to execute.
    :return: None.
    """
    # Connect to the database.
    database = sqlite3.connect(db)
    cursor = database.cursor()
    # Execute the command.
    cursor.execute(query)
    # Commit the changes.
    database.commit()
    cursor.close()


def authenticated(username, token):
    """
    Checks user database for the provided token.
    :param username: [string] the user's identification name.
    :param token: [string] the token granted to current users.
    :return: [bool] True if the username/token combination is valid, False otherwise.
    """
    query = ''
    result = query_db(USERS_DB, query)
    # There is a user with the given user and token combination, they are authenticated.
    if result:
        return True
    return False


def response(error=False, msg="1"):
    """
    Creates a JSON string. Defaults assume the operation completed successfully.
    :param error: [bool] True if there was an error, False otherwise.
    :param msg: [string] the message to provide to the user.
    :return: [string] a formatted JSON to notify the user of the outcome of the current process.
    """
    if error:
        resp = {"error": msg}
    else:
        resp = {"success": msg}

    return jsonify(resp)


@app.route('/', methods=['GET'])
def home():
    return "Apartment API. Created by Lukas Richters, 2020."


def check_registration_code(code):
    """
    Ensures the code is formatted correctly.
    :param code: [string] the code to check.
    :return: [bool] True if the code is formatted correctly, False otherwise.
    """
    # All codes are 5 5-letter words separated by hyphens. So, a valid code has 29 characters and
    # the 6th, 12th, 18th, and 24th characters are hyphens.
    if len(code) != 29:
        return False

    elif code[5] != '-' or code[11] != '-' or code[17] != '-' or code[23] != '-':
        return False

    return True


def valid_registration_code(code):
    """
    Checks the given registration code for existence in the database.
    :param code: [string] the code to check for.
    :return: [bool] True if the code is in the database, False otherwise.
    """
    # Ensure code doesn't have malicious SQL in it.
    if check_registration_code(code):
        query = 'SELECT code FROM registration_codes WHERE code="{}";'.format(code)
        result = query_db(USERS_DB, query)
        if len(result) == 1:
            return True

    return False


@app.route('/register', methods=['GET'])
def register():
    """
    Registers a user with the network.
    :return: [string] a JSON object with an error or success message.
    """
    # Ensure registration code, name, and email are provided in the request.
    if "code" in request.args and "name" in request.args and "email" in request.args:
        code = str(request.args["code"])
        name = str(request.args["name"])
        email = str(request.args["email"])
    # Error if any field is unfilled.
    else:
        return response(error=True, msg="Insufficient information.")

    # Check that the code is valid.
    if valid_registration_code(code):
        # Remove the registration code from the database so it cannot be used again.
        cmd = 'DELETE FROM registration_codes WHERE code="{}";'.format(code)
        modify_db(USERS_DB, cmd)
        # Add user to the database.
        cmd = 'INSERT INTO users VALUES ("{}", "{}", 1, 0, NULL);'.format(name, email)
        modify_db(USERS_DB, cmd)
        return provide_jwt(name, resident=True)

    else:
        return response(error=True, msg="The provided code is invalid.")


def generate_login_code():
    """
    Randomly generates a 5-digit number to use as a temporary login code for the user.
    :return: [int] the number generated to login with.
    """
    return randint(10000, 99999)


def generate_jwt(resident):
    """
    Generates a JWT for a newly logged-in user.
    :param resident: [bool] True if the user is a resident, False otherwise.
    :return: [bytes] a JWT-formatted byte string.
    """
    # The expiration time should be one day after the token is issued.
    exp_time = time.time() + 86400

    # Define headers.
    # alg: the algorithm being used for encryption (RSA-256).
    # typ: the format of the string (JWT).
    headers = {"alg": "RS256",
               "typ": "JWT"}

    # Define the payload.
    # exp: the expiration time of the token (24 hours from now).
    # res: True if the user is a resident, False otherwise.
    payload = {"exp": exp_time,
               "res": resident}

    return jwt.encode(payload, PRIVATE_KEY, algorithm='RS256', headers=headers)


def provide_jwt(name, resident=False):
    """
    Generates a JWT and returns it as an HTTPOnly cookie.
    :param name: [str] the name of the user.
    :param resident: [bool] True if the user is a resident, False otherwise.
    :return:
    """
    # Get a JWT for the user.
    token = generate_jwt(resident)
    # Add token to database.
    cmd = 'UPDATE users SET token="{}" WHERE name="{}";'.format(token, name)
    modify_db(USERS_DB, cmd)
    # Return the JWT in an HTTPOnly cookie.
    resp = make_response()
    resp.set_cookie('aptJWT', token, httponly=True)
    return resp


@app.route('/login', methods=['GET'])
def login():
    """
    Logs a user into the application. Handles both the name/email portion, and the final login using
    the emailed code.
    :return: [string] JSON data containing either a JWT or simple success message based on the login
    stage.
    """
    # 1st stage login; return a success message.
    if "name" in request.args and "email" in request.args:
        name = str(request.args["name"])
        email = str(request.args["email"])
        # Check that the user exists in the database.
        query = 'SELECT * FROM users WHERE name="{}" AND email="{}";'.format(name, email)
        result = query_db(USERS_DB, query)
        if len(result) == 1:
            # Get a login code for the user.
            login_code = generate_login_code()
            print(login_code)  # TODO: remove this line.
            # Add the login code to the database.
            cmd = 'UPDATE users SET login_code={} WHERE name="{}";'.format(login_code, name)
            modify_db(USERS_DB, cmd)
            # TODO: Send email to the user.
            return response()

        return response(error=True, msg='The name and email combination is invalid')

    # 2nd stage login; return JWT.
    elif "code" in request.args:
        # Ensure login code exists.
        query = 'SELECT * FROM users WHERE login_code={};'.format(str(int(request.args['code'])))
        result = query_db(USERS_DB, query)
        # If the user supplied a valid login code, give them a JWT.
        if len(result) == 1:
            # There will be only one result, first dict has the name.
            name = result[0]['name']
            # Remove the code from the database.
            cmd = 'UPDATE users SET login_code=NULL WHERE name="{}";'.format(name)
            modify_db(USERS_DB, cmd)
            # Return the JWT as an HTTPOnly cookie.
            return provide_jwt(name, True)

        return response(error=True, msg='Invalid login code.')

    else:
        return response(error=True, msg='There is insufficient data to log a user into the '
                                        'application')


@app.route('/login-guest', methods=['GET'])
def login_guest():
    """
    Logs a guest into the application.
    :return: A cookie with a JSON Web Token payload.
    """
    if 'name' in request.args:
        name = request.args['name']
        # Add guest to the database.
        cmd = 'INSERT INTO users VALUES ("{}", NULL, 0, 0, NULL);'.format(name)
        modify_db(USERS_DB, cmd)
        # Return JWT.
        return provide_jwt(name)

    return response(error=True, msg='There is insufficient data to log a user into the '
                                    'application')


if __name__ == '__main__':
    app.run()
