import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config['DEBUG'] = True

USERS_DB = './data/users.db'


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
    :return: [dict] the SQL response from the query.
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
        query = 'SELECT code FROM registration_codes WHERE code=' + code + ';'
        result = query_db(USERS_DB, query)
        if len(result) == 1:
            return True

    return False


@app.route('/register', methods=['POST'])
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
        query = 'DELETE FROM registration_codes WHERE code=' + code + ';'
        modify_db(USERS_DB, query)

        # Add user to the database.
        query = 'INSERT INTO users VALUES (' + name + ', ' + email + ')'
        modify_db(USERS_DB, query)

    else:
        return response(error=True, msg="The provided code is invalid.")


if __name__ == '__main__':
    app.run()
