import json
import os

class HistoryManager:
    def __init__(self, history_file='sent_posts_history.json'):
        self.history_file = history_file
        self.sent_history = self._load_history()

    def _load_history(self):
        try:
            # Create file if it doesn't exist
            if not os.path.exists(self.history_file):
                with open(self.history_file, 'w') as f:
                    json.dump({"users": {}}, f)
                return {"users": {}}
            
            # Try to load existing file
            with open(self.history_file, 'r') as f:
                content = f.read().strip()
                if not content:  # If file is empty
                    default_data = {"users": {}}
                    json.dump(default_data, open(self.history_file, 'w'))
                    return default_data
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            # Handle any JSON errors by creating new history
            default_data = {"users": {}}
            with open(self.history_file, 'w') as f:
                json.dump(default_data, f)
            return default_data

    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.sent_history, f, indent=4)

    def update_history(self, user, post_url):
        self.sent_history["users"].setdefault(user, []).append(post_url)
        self._save_history()

    def has_shared_with_user(self, user, post_url):
        return post_url in self.sent_history["users"].get(user, [])

