from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class HashPassword:
    
    def __init__(self):
        self.password_Hasher = PasswordHasher()
    
    def hash_password(self, password):
        return self.password_Hasher.hash(password)
    
    def verify_password(self, password, hashed):
        try:
            self.password_Hasher.verify(password, hashed)
            return True
        except VerifyMismatchError:
            return False