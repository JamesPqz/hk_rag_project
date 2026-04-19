import json

from backend.cache.redis_client import redis_client


class ConversationService:
    def __init__(self, session_id:str,  max_history:int = 10):
        self.session_id = session_id
        self.key = f"conv:{session_id}"
        self.max_history = max_history

    def add_message(self, role: str , content: str):
        history = self.get_history()
        history.append({'role': role, "content": content})
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        redis_client.set(self.key, json.dumps(history))

    def get_history(self) -> list:
        data = redis_client.get(self.key)
        return json.loads(data) if data else []

    def clear(self):
        redis_client.delete(self.key)