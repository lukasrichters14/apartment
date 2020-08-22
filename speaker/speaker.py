import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Speaker:

    def __init__(self, name):
        """
        Establish a connection to Spotify.
        :param name: [str] The name of the device (speaker) to connect to.
        """
        # Scope essentially determines what permissions Spotify grants to the app.
        SCOPE = "user-read-playback-state user-modify-playback-state"
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
                speaker_id = devices['id']

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

    def play(self, spotify_uri, playlist=False):
        """
        Play the given song over the speaker.
        :param spotify_uri: [str] the Spotify URI representing the song to be played.
        :param playlist: [bool] True if spotify_uri is a playlist, False if it is just a song.
        """
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
        track = self.sp.currently_playing()['item']  # Current song object.
        # Take only the relevant data: name, album, artist.
        track_dict = {'name': track['name'],
                      'album': track['album'],
                      'artist': track['artist']
                      }
        return track_dict

    def shuffle(self, state):
        """
        Toggle the shuffle state.
        :param state: [bool] True to turn shuffle on, False to turn shuffle off.
        """
        self.sp.shuffle(state=state)

    def search(self, query):
        """
        Search for a song on Spotify.
        :param query: [str] the song to search for.
        :return: [dict] {song: Spotify URI}
        """
        # Get the results from the Spotify search query.
        result = self.sp.search(query)
        tracks_dict = {}

        # Get the song name and uri from the list of track objects.
        for track in result:
            name = track['name']
            uri = track['uri']
            tracks_dict[name] = uri

        return tracks_dict

    def add_to_queue(self, song):
        """
        Add a song to the queue.
        :param song: [str] a Spotify URI.
        """
        self.sp.add_to_queue(song)
