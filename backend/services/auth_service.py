class AuthService:
    def __init__(self, secret_key, algorithm, expiration_hours):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours

    def verify_token(self, token):
        # placeholder for demo
        return True