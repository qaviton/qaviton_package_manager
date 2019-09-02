import json
from cryptography.fernet import Fernet


def encrypt(**kwargs):
    key = Fernet.generate_key()
    token = Fernet(key).encrypt(json.dumps(kwargs).encode('utf-8'))
    return key, token


def decypt(key, token)->dict:
    return json.loads(Fernet(key).decrypt(token).decode('utf-8'))
