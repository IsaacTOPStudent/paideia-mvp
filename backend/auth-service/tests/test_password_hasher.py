from src.infrastructure.adapters.password_hasher import DjangoPasswordHasher

class TestPasswordHasher:

    def setup_method(self):
        self.hasher = DjangoPasswordHasher()

    def test_should_hash_password(self):
        password = "Password123*"

        hashed = self.hasher.hash(password)

        assert hashed is not None
        assert hashed != password
        assert isinstance(hashed, str)

    def test_should_verify_correct_password(self):
        password = "Password123*"

        hashed = self.hasher.hash(password)

        assert self.hasher.verify(password, hashed) is True

    def test_should_reject_invalid_password(self):
        password = "Password123*"
        wrong_password = "WrongPassword123*"

        hashed = self.hasher.hash(password)

        assert self.hasher.verify(wrong_password, hashed) is False

    def test_same_password_generates_different_hashes(self):
        password = "Password123*"

        hash1 = self.hasher.hash(password)
        hash2 = self.hasher.hash(password)

        assert hash1 != hash2