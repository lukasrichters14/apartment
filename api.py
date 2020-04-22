import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config['DEBUG'] = True


@app.route('/', methods=['GET'])
def home():
    pass


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registers a user with the network.
    :return:
    """
    pass


if __name__ == '__main__':
    app.run()
