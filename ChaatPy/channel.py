import datetime
from ChaatPy.client import Client
from ChaatPy.request import Request
from ChaatPy.message import Message, FetchedMessage

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
    
    async def fetch_messages(self):
        data = {
            'action': 'fetchData',
            'hash': self.hash,
            'csrf_token_check': self.client.cstftoken,
            'mode': 'log',
            'type': 'last',
            'num': '0',
        }

        send = await self.request.room_post(data)

        msgs = []

        for s in send['data_list'].values():
            msgs.append(FetchedMessage(s))

        return msgs
    
    def generate_timestamp(self, time: datetime.datetime):
        return time.strftime("%Y%m%d%H%M%S")

    async def fetch_message(self, num: str):
        data = {
            'action': 'fetchData',
            'hash': self.hash,
            'csrf_token_check': self.client.cstftoken,
            'mode': 'log',
            'type': 'last',
            'num': num,
        }

        send = await self.request.room_post(data)
        
        for s in send['data_list']:
            return FetchedMessage(s)
    
    async def getMembers(self):
        data = {
            'action': 'getMembers',
            'hash': self.hash,
            'csrf_token_check': self.client.cstftoken,
        }

        send = await self.request.room_post(data)

        return send