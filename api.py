import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config['DEBUG'] = True

USERS_DB = 'users.db'


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


def authenticated(username, token):
    """
    Checks user database for the provided token.
    :param username: [string] the user's identification name.
    :param token: [string] the token granted to current users.
    :return: [bool] True if the username/token combination is valid, False otherwise.
    """
    # Connect to the users database.
    database = sqlite3.connect(USERS_DB)
    # Set the format of the return of the SQL query.
    database.row_factory = create_dict
    cursor = database.cursor()
    # Form the SQL query.
    query = ''
    result = cursor.execute(query).fetchall()
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
    return "Apartment API"


@app.route('/register', methods=['POST'])
def register():
    """
    Registers a user with the network.
    :return: [string] a JSON object with an error or success message.
    """
    # Ensure registration code is in the request.
    if "code" in request.args:
        code = str(request.args["code"])
    # Error if no code.
    else:
        return response(error=True, msg="No code provided.")

    # TODO: check that the given code is in the database.


if __name__ == '__main__':
    app.run()
