import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_API_URL = "https://slack.com/api"

headers = {
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    "Content-Type": "application/json"
}

def send_slack_message(channel: str, text: str, thread_ts: str = None):
    payload = {
        "channel": channel,
        "text": text
    }
    if thread_ts:
        payload["thread_ts"] = thread_ts

    response = httpx.post(f"{SLACK_API_URL}/chat.postMessage", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
