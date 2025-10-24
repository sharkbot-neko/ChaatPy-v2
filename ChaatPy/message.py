import json

class SendedMessage:
    def __init__(self, data: str):
        self.data = data
        self.json_data = json.loads(data)

        self.content = self.json_data.get('msg', None)
        self.message_type = self.json_data.get('type', None)

class Message:
    def __init__(self, data: dict):
        self.data = data

        self.msg = self.data.get('msg', None)
        self.message_type = self.data.get('type', None)
        self.name = self.data.get('name', None)
        self.user_id = self.data.get('userid', None)
        self.date = self.data.get('date', None)

    def to_json(self):
        return self.data