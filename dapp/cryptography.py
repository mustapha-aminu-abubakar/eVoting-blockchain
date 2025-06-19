from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

# Load secret key
FERNET_KEY = os.environ.get("FERNET_KEY")
fernet = Fernet(FERNET_KEY)


def encrypt_object(obj: str) -> str:
    """
    Encrypts a string object using Fernet symmetric encryption.

    Args:
        obj (str): The string to encrypt.

    Returns:
        str: The encrypted string, base64-encoded.
    """
    return fernet.encrypt(obj.encode()).decode()


def decrypt_object(encrypted_key: str) -> str:
    """
    Decrypts a Fernet-encrypted string back to its original form.

    Args:
        encrypted_key (str): The encrypted, base64-encoded string to decrypt.

    Returns:
        str: The decrypted original string.
    """
    return fernet.decrypt(encrypted_key).decode()
