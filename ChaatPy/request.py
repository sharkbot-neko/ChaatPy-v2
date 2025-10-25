from ChaatPy.client import Client
import orjson

class Request:
    def __init__(self, client: Client):
        self.client = client
        pass

    async def room_post(self, data: dict):
        async with self.client.session.post('https://c.kuku.lu/room.php', data=data) as page:
            return orjson.loads(await page.text())