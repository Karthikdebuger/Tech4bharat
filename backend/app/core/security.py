"""Security primitives: Argon2id password hashing, TOTP, and HMAC pseudonyms.

Per §7.1 and ADR-0007:
- Passwords hashed with Argon2id.
- TOTP (RFC 6238) support for manager/owner roles.
- Customer reference pseudonym: HMAC-SHA256(secret, customer_id).
- Constant-time comparison for sensitive tokens.
"""

import hmac
import hashlib
import secrets
from typing import Final
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import pyotp

_hasher: Final[PasswordHasher] = PasswordHasher(
    time_cost=2,
    memory_cost=65536,  # 64 MiB
    parallelism=1,
    hash_len=32,
    salt_len=16,
)

def hash_password(password: str) -> str:
    """Hash plaintext password using Argon2id."""
    return _hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify plaintext password against an Argon2id hash."""
    try:
        return _hasher.verify(hashed_password, password)
    except VerifyMismatchError:
        return False

def generate_totp_secret() -> str:
    """Generate RFC 6238 base32 TOTP secret."""
    return pyotp.random_base32()

def verify_totp(secret: str, code: str) -> bool:
    """Verify 6-digit TOTP code with standard 30s window."""
    totp = pyotp.TOTP(secret)
    return bool(totp.verify(code, valid_window=1))

def generate_session_token() -> str:
    """Generate cryptographically secure 256-bit session token."""
    return secrets.token_urlsafe(32)

def generate_customer_pseudonym(server_secret: bytes, customer_identifier: str) -> str:
    """Compute pseudonymous HMAC-SHA256 customer reference.

    Ensures raw customer PII never leaks into public receipts or audit records.
    """
    digest = hmac.new(
        server_secret,
        customer_identifier.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"c_{digest[:16]}"
