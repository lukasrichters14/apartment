from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Key names.
PUBLIC_KEY_FILE_NAME = 'public-key.pem'
PRIVATE_KEY_FILE_NAME = 'private-key.pem'


def main():
    # Generate a private key.
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    # Generate a public key from the private key.
    public_key = private_key.public_key()

    # Store private key in PEM format.
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Store public key in PEM format.
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Save private key to file.
    with open(PRIVATE_KEY_FILE_NAME, 'wb') as f:
        f.write(private_pem)

    # Save public key to file.
    with open(PUBLIC_KEY_FILE_NAME, 'wb') as f:
        f.write(public_pem)


if __name__ == "__main__":
    main()
