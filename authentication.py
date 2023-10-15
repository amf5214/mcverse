from passlib.hash import sha256_crypt


def create_password(password_string):
    return sha256_crypt.encrypt(password_string)

def validate_password(given_pass, real_pass):
    return sha256_crypt.verify(given_pass, real_pass)