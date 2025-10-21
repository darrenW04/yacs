from passlib.context import CryptContext

# 1. Create a password context ONCE
# This specifies the hashing algorithm to use
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)