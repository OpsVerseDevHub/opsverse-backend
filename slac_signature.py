import hmac
import hashlib

# Your Slack signing secret (replace or load from .env)
signing_secret = b'8f7617efec54036769b227f8a967721a'

# Take inputs
timestamp = input("Enter Slack timestamp: ").strip()
body = input("Enter raw JSON body (as sent in Postman): ").strip()

# Construct base string per Slack's spec
base_string = f'v0:{timestamp}:{body}'

# Generate HMAC-SHA256 hash
hashed = hmac.new(signing_secret, base_string.encode('utf-8'), hashlib.sha256).hexdigest()

# Full signature value
signature = f'v0={hashed}'

print(f"\nGenerated Slack Signature:\n{signature}\n")