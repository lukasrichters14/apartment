import sys
import flask
from flask import request, jsonify, make_response
from flask_cors import CORS
import sqlite3

sys.path.append('./security')
from speaker import Speaker
from security import SecurityController

app = flask.Flask(__name__)
app.config['DEBUG'] = True
CORS(app)  # Prevent CORS errors.

# Databases.
USERS_DB = './data/users.db'
SPOTIFY_DB = './data/spotify.db'

# Control classes
sp = Speaker('Pixel 3')
sc = SecurityController()


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


def query_db(db, query, fetch_multiple=False):
    """
    Performs an SQL query on a database.
    :param db: [string] the file path to the database.
    :param query: [string] an SQL-formatted query to the database.
    :param fetch_multiple: [bool] True if multiple rows should be returned from the database, False
    if only one row should be returned.
    :return: [list] the SQL response from the query.
    """
    # Connect to the database.
    database = sqlite3.connect(db)
    # Set the format of the return of the SQL query.
    database.row_factory = create_dict
    cursor = database.cursor()
    if fetch_multiple:
        result = cursor.execute(query).fetchall()
    else:
        result = cursor.execute(query).fetchone()
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


def authenticated(request_obj, resident_page=True):
    """
    Checks user database for the provided token.
    :param request_obj: the Flask request object.
    :param resident_page: [bool] True if the page requires a resident account.
    :return: [bool] True if the user has access to this page, False otherwise.
    """
    token = request_obj.cookies.get('aptJWT')
    query = 'SELECT * FROM users WHERE token="{}";'.format(token)
    result = query_db(USERS_DB, query, True)
    # Token exists.
    if len(result) == 1:
        if result[0]['resident'] == 0 and resident_page is True:
            return False
        return True
    return False


def response(error=False, msg="200 OK"):
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
        result = query_db(USERS_DB, query, True)
        if len(result) == 1:
            return True

    return False


@app.route('/register', methods=['POST'])
def register():
    """
    Registers a user with the network.
    :return: [string] a JSON object with an error or success message.
    """
    post_data = request.get_json()
    # Ensure registration code, name, and email are provided in the request.
    if "code" in post_data and "name" in post_data and "email" in post_data:
        code = str(post_data["code"])
        name = str(post_data["name"])
        email = str(post_data["email"])
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


def provide_jwt(name, resident=False):
    """
    Generates a JWT and returns it as an HTTPOnly cookie.
    :param name: [str] the name of the user.
    :param resident: [bool] True if the user is a resident, False otherwise.
    :return:
    """
    # Get a JWT for the user.
    token = sc.generate_jwt(resident)
    # Add token to database.
    cmd = 'UPDATE users SET token="{}" WHERE name="{}";'.format(token, name)
    modify_db(USERS_DB, cmd)
    # Return the JWT in an HTTPOnly cookie.
    resp = make_response()
    resp.set_cookie('aptJWT', token, httponly=True)
    return resp


@app.route('/login', methods=['POST'])
def login():
    """
    Logs a user into the application. Handles both the name/email portion, and the final login using
    the emailed code.
    :return: [string] JSON data containing either a JWT or simple success message based on the login
    stage.
    """
    post_data = request.get_json()
    # 1st stage login; return a success message.
    if "name" in post_data and "email" in post_data:
        name = str(post_data["name"])
        email = str(post_data["email"])
        # Check that the user exists in the database.
        query = 'SELECT * FROM users WHERE name="{}" AND email="{}";'.format(name, email)
        result = query_db(USERS_DB, query, True)
        if len(result) == 1:
            # Get a login code for the user.
            login_code = sc.generate_login_code()
            print(login_code)  # TODO: remove this line.
            # Add the login code to the database.
            cmd = 'UPDATE users SET login_code={} WHERE name="{}";'.format(login_code, name)
            modify_db(USERS_DB, cmd)
            # TODO: Send email to the user.
            return response()

        return response(error=True, msg='The name and email combination is invalid')

    # 2nd stage login; return JWT.
    elif "code" in post_data:
        # Ensure login code exists.
        query = 'SELECT * FROM users WHERE login_code={};'.format(str(int(post_data['code'])))
        result = query_db(USERS_DB, query, True)
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


@app.route('/login-guest', methods=['POST'])
def login_guest():
    """
    Log a guest into the application.
    :return: A cookie with a JSON Web Token payload.
    """
    post_data = request.get_json()
    if 'name' in post_data:
        name = post_data['name']
        # Add guest to the database.
        cmd = 'INSERT INTO users VALUES ("{}", NULL, 0, 0, NULL);'.format(name)
        modify_db(USERS_DB, cmd)
        # Return JWT.
        return provide_jwt(name)

    return response(error=True, msg='There is insufficient data to log a user into the '
                                    'application')


# Spotify Endpoints.
@app.route('/spotify/play', methods=['POST', 'PUT'])
def spotify_play():
    """
    Play a song or playlist.
    :return:
    """
    # Start playback.
    if request.method == 'POST':
        post_data = request.get_json()

        if 'uri' in post_data and 'playlist' in post_data:
            uri = post_data['uri']
            playlist = post_data['playlist']
            sp.play(uri, playlist, resume=False)  # Play the requested song.
            return response()  # Respond with a success.

        return response(error=True, msg='A URI must be given to play the song.')

    # Resume playback.
    elif request.method == 'PUT':
        sp.play(resume=True)
        return response()


@app.route('/spotify/pause', methods=['PUT'])
def spotify_pause():
    """
    Pause the playback on the active device.
    :return:
    """
    sp.pause()
    return response()


@app.route('/spotify/currently-playing', methods=['GET'])
def spotify_currently_playing():
    """
    Get the song that is currently playing.
    :return: [str] JSON-formatted track object.
    """
    cp = sp.currently_playing()
    # Check if there is a currently playing track.
    if cp:
        return jsonify(cp)
    return response(error=True, msg='There is not a currently playing track.')


@app.route('/spotify/shuffle', methods=['PUT'])
def spotify_shuffle():
    """
    Shuffle the current playlist.
    :return:
    """
    put_data = request.get_json()  # Retrieve JSON data.
    sp.shuffle(put_data['state'])  # Set the shuffle state to the 'state' value.
    return response()


@app.route('/spotify/search', methods=['GET'])
def spotify_search():
    """
    Search for a song on Spotify.
    :return:
    """
    if 'query' in request.args:
        query = request.args['query']
        return jsonify(sp.search(query))

    return response(error=True, msg='Invalid query.')


@app.route('/spotify/add-to-queue', methods=['POST'])
def spotify_add_to_queue():
    """
    Add a song to the queue.
    :return:
    """
    post_data = request.get_json()
    if 'uri' in post_data:
        uri = post_data['uri']
        sp.add_to_queue(uri)
        return response()

    return response(error=True, msg='Must provide a valid Spotify URI.')


@app.route('/spotify/playlists', methods=['GET'])
def spotify_playlists():
    """
    Get the playlists for the current user.
    """
    return jsonify(sp.get_playlists())


if __name__ == '__main__':
    app.run()
