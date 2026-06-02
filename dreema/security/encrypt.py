"""Encryption and random utility helpers for Dreema."""

import random
import string
import secrets
import bcrypt

class Encrypt:
    """Utility class for generating secrets, hashes, and random strings."""

    """
        Generate a random string of a given length and character type.

        type :
                1 - numbers only
                2 - text only
                3 - text and numbers
                4 - text and numbers and symbols
    """
    @staticmethod
    def generateRandom(length: int = 10, type: int = 4):
        """Return a random string based on the requested character set."""
        if type == 1:
            chars = string.digits
        elif type == 2:
            chars = string.ascii_letters
        elif type == 3:
            chars = string.ascii_letters + string.digits
        elif type == 4:
            chars = string.ascii_letters + string.digits + string.punctuation
        else:
            chars = string.ascii_letters + string.digits + string.punctuation

        return ''.join(random.choices(chars, k=length))
    
    @staticmethod
    def getSecret(bytelength: int = 32):
        """Return a secure hex string suitable for use as a secret."""
        secret = secrets.token_hex(bytelength)
        return secret
    
    @staticmethod
    def hash(password: str, rounds: int = 10):
        """Hash a password using bcrypt with the provided round count."""
        hashedPwd = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=rounds))
        return hashedPwd.decode()

    @staticmethod
    def verifyHash(password: str, hash: str):
        """Verify a bcrypt hash against a plain password."""
        try:
            if not bcrypt.checkpw(password.encode(), hash.encode()):
                return False

            return True
        except Exception:
            return False