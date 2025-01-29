import json

class HistoryManager:
    def __init__(self, history_file='sent_posts_history.json'):
        self.history_file = history_file
        self.sent_history = self._load_history()

    def _load_history(self):
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"users": {}}

    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.sent_history, f, indent=4)

    def update_history(self, user, post_url):
        self.sent_history["users"].setdefault(user, []).append(post_url)
        self._save_history()

    def has_shared_with_user(self, user, post_url):
        return post_url in self.sent_history["users"].get(user, [])

