from django.contrib.auth.hashers import make_password, check_password

class DjangoPasswordHasher:
    """
    Adapter: Django's built-in password hasher
    """

    @staticmethod
    def hash(password: str) -> str:
        return make_password(password)
    
    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        return check_password(password, hashed)