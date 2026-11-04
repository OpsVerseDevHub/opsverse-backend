import json
from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self._connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self._connections.pop(user_id, None)

    async def broadcast(self, event: dict):
        payload = json.dumps(event)
        dead = []
        for uid, ws in self._connections.items():
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(uid)
        for uid in dead:
            self.disconnect(uid)

    async def send_to(self, user_id: int, event: dict):
        ws = self._connections.get(user_id)
        if ws:
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                self.disconnect(user_id)


manager = ConnectionManager()
