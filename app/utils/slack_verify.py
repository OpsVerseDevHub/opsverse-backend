import hmac
import hashlib
import time
from fastapi import Request, HTTPException
import os

SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

def verify_slack_signature(request: Request, body: bytes):
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_signature = request.headers.get("X-Slack-Signature")

    if not timestamp or not slack_signature:
        raise HTTPException(status_code=400, detail="Missing Slack headers")

    # Protect against replay attacks
    if abs(time.time() - int(timestamp)) > 60 * 5:
        raise HTTPException(status_code=403, detail="Request too old")

    sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(my_signature, slack_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
