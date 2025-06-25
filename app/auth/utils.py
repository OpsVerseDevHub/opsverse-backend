from passlib.context import CryptContext
import hmac
import hashlib
import os
from dotenv import load_dotenv

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

load_dotenv()
GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

def verify_github_signature(payload_body: bytes, signature: str) -> bool:
    if not GITHUB_SECRET:
        return False
    expected = 'sha256=' + hmac.new(GITHUB_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
