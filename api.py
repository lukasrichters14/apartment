import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config['DEBUG'] = True


@app.route('/', methods=['GET'])
def home():
    pass


@app.route('/register', methods=['POST'])
def register():
    """
    Registers a user with the network.
    :return:
    """
    # Ensure registration code and mac address are in the request
    if "code" in request.args and "mac" in request.args:
        code = str(request.args["code"])
        mac = str(request.args["mac"])
    # Error if the API call is incorrect.
    else:
        return "Error: No id field provided. Please specify an id."


if __name__ == '__main__':
    app.run()
