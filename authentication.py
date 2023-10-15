from passlib.hash import sha256_crypt
from datetime import datetime, timedelta

def create_password(password_string):
    return sha256_crypt.encrypt(password_string)

def validate_password(given_pass, real_pass):
    return sha256_crypt.verify(given_pass, real_pass)

def encode_auth_token(email_account):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
                'iat': datetime.utcnow(),
                'sub': email_account
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e
        