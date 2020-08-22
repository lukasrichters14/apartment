import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import time
from random import randint


class SecurityController:
    """
    SecurityController compartmentalizes the various security measures used by the API. It manages
    the public/private key pair for RSA encryption of the JWT. Additionally, it handles generating
    the random login code for residents.
    """

    def __init__(self):
        PUBLIC_KEY_FILE_NAME = './keys/public-key.pem'
        PRIVATE_KEY_FILE_NAME = './keys/private-key.pem'
        self.PRIVATE_KEY = SecurityController._get_private_key(PRIVATE_KEY_FILE_NAME)
        self.PUBLIC_KEY = SecurityController._get_public_key(PUBLIC_KEY_FILE_NAME)

    @staticmethod
    def _get_private_key(file_name):
        """
        Read private key from a file.
        :param file_name: [str] the file where the private key is stored.
        :return: [str] the private key.
        """
        with open(file_name, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

        return private_key

    @staticmethod
    def _get_public_key(file_name):
        """
        Read public key from a file.
        :param file_name: [str] the file where the public key is stored.
        :return: [str] the public key.
        """
        with open(file_name, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

        return public_key

    def generate_jwt(self, resident):
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

        return jwt.encode(payload, self.PRIVATE_KEY, algorithm='RS256', headers=headers)

    @staticmethod
    def generate_login_code():
        """
        Randomly generates a 5-digit number to use as a temporary login code for the user.
        :return: [int] the number generated to login with.
        """
        return randint(10000, 99999)

