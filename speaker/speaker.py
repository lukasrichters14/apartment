import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Speaker:

    def __init__(self, name):
        """
        Establish a connection to Spotify.
        :param name: [str] The name of the device (speaker) to connect to.
        """
        # Scope essentially determines what permissions Spotify grants to the app.
        SCOPE = "user-read-playback-state"
        # Establish a connection with Spotify.
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE,
                                                            username='lukasrichters14'))
        # Get the device id for the speaker.
        self.speaker_id = self._connect_device(name)

    def play(self, spotify_uri):
        """
        Play the given song over the speaker.
        :param spotify_uri: [str] the Spotify URI representing the song to be played.
        """
        # Start playback.
        # Exterior functions will deal with exactly what to play. This function just plays the given
        # URI.
        self.sp.start_playback(device_id=self.speaker_id, uris=[spotify_uri])

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
