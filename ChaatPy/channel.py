from ChaatPy.client import Client
from ChaatPy.request import Request
from ChaatPy.message import Message

import json

class Channel:
    def __init__(self, client: Client, hash: str):
        self.request = Request(client) 
        self.client = client
        self.hash = hash
        pass

    def url(self):
        return f"https://c.kuku.lu/{self.hash}"

    async def send(self, message: Message):
        data = {
            'action': 'sendData',
            'hash': self.hash,
            'profile_name': '匿名さかなくん',
            'profile_color': '#000000',
            'data': json.dumps(message.data),
            'csrf_token_check': self.client.cstftoken,
        }

        send = await self.request.room_post(data)

        return send
    
    async def getMembers(self):
        data = {
            'action': 'getMembers',
            'hash': self.hash,
            'csrf_token_check': self.client.cstftoken,
        }

        send = await self.request.room_post(data)

        return send