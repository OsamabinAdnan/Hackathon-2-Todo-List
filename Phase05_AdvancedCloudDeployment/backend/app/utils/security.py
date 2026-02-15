import bcrypt
import hashlib
import base64

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    # Convert password to bytes
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')

    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    # Handle bcrypt's 72-byte password length limit by using SHA256 + base64 for long passwords
    if len(plain_password) > 72:
        # Hash the long password using SHA256, base64 encode it, then check against bcrypt hash
        plain_password = base64.b64encode(hashlib.sha256(plain_password).digest())

    return bcrypt.checkpw(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a hash for a plain password."""
    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # Handle bcrypt's 72-byte password length limit by using SHA256 + base64 for long passwords
    if len(password_bytes) > 72:
        # Hash the long password using SHA256, then base64 encode it before bcrypt hashing
        # This prevents NULL byte issues in the bcrypt hashing
        password_bytes = base64.b64encode(hashlib.sha256(password_bytes).digest())

    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')