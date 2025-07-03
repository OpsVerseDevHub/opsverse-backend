import time
import hmac
import hashlib
import json
import os
SLACK_SIGNING_SECRET = "8f7617efec54036769b227f8a967721a"  # Replace with your real secret
URL = "http://127.0.0.1:8000/webhooks/slack"  # Your FastAPI endpoint
# Example JSON payload
payload = {
    "project_id": 1,
    "slack_channel_id": "C092HAFBNTU"
}
def generate_signature(secret, timestamp, body):
    sig_basestring = f'v0:{timestamp}:{body}'.encode()
    my_signature = 'v0=' + hmac.new(
        secret.encode(),
        sig_basestring,
        hashlib.sha256
    ).hexdigest()
    return my_signature
def main():
    timestamp = str(int(time.time()))
    body_str = json.dumps(payload, separators=(',', ':'))
    signature = generate_signature(SLACK_SIGNING_SECRET, timestamp, body_str)
    curl_cmd = f"""curl -X POST {URL} \\
 -H "Content-Type: application/json" \\
 -H "x-slack-request-timestamp: {timestamp}" \\
 -H "x-slack-signature: {signature}" \\
 -d '{body_str}'"""
    print("\nGenerated curl command:\n")
    print(curl_cmd)
if __name__ == "__main__":
    main()