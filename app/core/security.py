import bcrypt
import jwt
from datetime import datetime, timedelta, timezone


# --- JWT CONFIGURATION ---
# In production, this MUST be a highly secure random string stored in a .env file.
# For local development, we will hardcode a secret key here.
SECRET_KEY = "super_secret_smart_vidhyalai_local_key_do_not_use_in_prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


def get_password_hash(password: str) -> str:
    """Converts a plain text password into a secure hash using pure bcrypt."""
    # Bcrypt requires passwords to be converted to bytes before hashing
    pwd_bytes = password.encode("utf-8")

    # Generate a secure salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)

    # Decode back to a string so it can be saved in PostgreSQL easily
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against the stored database hash."""
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(
        password=password_byte_enc, hashed_password=hashed_password_bytes
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a secure JSON Web Token (JWT) for the user."""
    to_encode = data.copy()

    # Set the expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # Cryptographically sign the token using our secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
