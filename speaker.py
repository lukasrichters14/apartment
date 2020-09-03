import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Speaker:

    def __init__(self, name):
        """
        Establish a connection to Spotify.
        :param name: [str] The name of the device (speaker) to connect to.
        """
        # Scope essentially determines what permissions Spotify grants to the app.
        SCOPE = "user-read-playback-state user-modify-playback-state playlist-read-private " \
                "playlist-read-collaborative "
        # Establish a connection with Spotify.
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE,
                                                            username='lukasrichters14'))
        # Get the device id for the speaker.
        self.speaker_id = self._connect_device(name)

    def _connect_device(self, name):
        """
        Manage the connection to the speaker.
        :param name: [str] the name of the device to connect to.
        :return: [str] the Spotify device id of the speaker.
        """
        speaker_id = ''

        # Retrieve a list of devices from Spotify.
        devices = self.sp.devices()['devices']
        # Get the device id for the requested device.
        if len(devices) == 1:
            # One device found, check if it is the requested device.
            if devices[0]['name'] == name:
                speaker_id = devices[0]['id']

        elif len(devices) > 1:
            # Multiple devices found, search for the correct one.
            for device in devices:
                if device['name'] == name:
                    speaker_id = device['id']
        else:
            raise RuntimeError('{} is unavailable.'.format(name))

        # Check if the device was found.
        if not speaker_id:
            raise RuntimeError('{} is unavailable.'.format(name))

        return speaker_id

    def play(self, spotify_uri='', playlist=False, resume=False):
        """
        Play the given song over the speaker.
        :param spotify_uri: [str] the Spotify URI representing the song to be played.
        :param playlist: [bool] True if spotify_uri is a playlist, False if it is just a song.
        :param resume: [bool] True if Spotify needs to resume the currently playing track, False
        otherwise.
        """
        # Resume playback.
        if resume:
            self.sp.start_playback()

        # Start playback.
        else:
            # Start playback on the speaker.
            if playlist:
                # Start a playlist.
                self.sp.start_playback(device_id=self.speaker_id, context_uri=spotify_uri)
            else:
                # Play a single song.
                self.sp.start_playback(device_id=self.speaker_id, uris=[spotify_uri])

    def pause(self):
        """
        Pause the playback on the speaker.
        """
        self.sp.pause_playback(device_id=self.speaker_id)

    def currently_playing(self):
        """
        Get the currently playing track.
        :return: [dict] information about the track that is playing.
        """
        track = self.sp.currently_playing()
        # If there is a currently playing track.
        if track:
            track = track['item']  # Current song object.
            # Take only the relevant data.
            track_dict = {'name': track['name'],  # Track name.
                          'album': track['album']['name'],  # Album name.
                          'artist': track['artists'][0]['name'],  # Artist name.
                          'artwork': track['album']['images'][1]['url']}  # Artwork URL.
            return track_dict

    def shuffle(self, state):
        """
        Toggle the shuffle state.
        :param state: [bool] True to turn shuffle on, False to turn shuffle off.
        """
        if state:
            state = 'true'
        else:
            state = 'false'
        self.sp.shuffle(state=state)

    def search(self, query):
        """
        Search for a song on Spotify.
        :param query: [str] the song to search for.
        :return: [dict] {song: Spotify URI}
        """
        # Get the results from the Spotify search query.
        result = self.sp.search(query)
        tracks_list = []
        # Get the song name and uri from the list of track objects.
        for track in result['tracks']['items']:
            name = track['name']  # Track name.
            uri = track['uri']  # Track URI.
            artist = track['artists'][0]['name']  # Artist name.
            tracks_list.append({
                'name': name,
                'uri': uri,
                'artist': artist
            })

        return tracks_list

    def add_to_queue(self, song):
        """
        Add a song to the queue.
        :param song: [str] a Spotify URI.
        """
        self.sp.add_to_queue(song)

    def get_playlists(self):
        """
        Return a list of playlists.
        """
        playlists = []
        result = self.sp.current_user_playlists()
        for playlist in result['items']:
            playlists.append({'name': playlist['name'],
                              'uri': playlist['uri']})
        return playlists

