import json
import re
import aiohttp
import asyncio
import base64
import uuid
import inspect

CookieToken = re.compile(r'[a-zA-Z0-9+/=]{88}')
CSRFToken = re.compile(r'[0-9a-fA-F]{32}')

class Client:
    def __init__(self):
        self.cookie_token = None
        self.room_id = None
        self.user_id = None
        self.user_name = None
        self.sec_websocket_key = base64.b64encode(uuid.uuid4().bytes).decode('utf-8')
        self.session = None
        self.cstftoken = None

        self.listeners = {}
        pass

    async def close(self):
        self.session.close()

    async def create_session(self):
        self.session = aiohttp.ClientSession()

    def getChannel(self, hash: str):
        from ChaatPy.channel import Channel
        return Channel(self, hash)
    
    def getRequest(self):
        from ChaatPy.request import Request
        
        return Request(self) 

    async def getCSTFToken(self):
        async with self.session.get(f'https://c.kuku.lu/') as page:
            page_text = await page.text()
            c = CSRFToken.search(page_text)
            self.cstftoken = c.group(0)
            return c.group(0)

    async def createRoom(self):
        data = {
            'action': 'createRoom',
            'csrf_token_check': self.cstftoken,
        }

        async with self.session.post(f'https://c.kuku.lu/api_server.php', data=data) as page:
            from ChaatPy.channel import Channel
            js = await page.json()
            return Channel(self, js['hash'])


    def event(self, func):
        event_name = func.__name__
        self.listeners.setdefault(event_name, []).append(func)
        return func

    async def dispatch(self, event_name, *args, **kwargs):
        if event_name not in self.listeners:
            return

        tasks = []
        for listener in self.listeners[event_name]:
            try:
                if inspect.iscoroutinefunction(listener):
                    tasks.append(asyncio.create_task(listener(*args, **kwargs)))
                else:
                    loop = asyncio.get_running_loop()
                    tasks.append(loop.run_in_executor(None, listener, *args))
            except Exception as e:
                print(f"[Error registering listener {listener.__name__}]: {e}")

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result, listener in zip(results, self.listeners[event_name]):
                if isinstance(result, Exception):
                    print(f"[Error in {listener.__name__}]: {result}")

    async def join(self, room: str):
        headers_join = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://c.kuku.lu/',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        }
        async with self.session.get(f'https://c.kuku.lu/{room}', headers=headers_join) as page:
            pattern = r"[a-zA-Z0-9+/=]{88}"
            self.cookie_token = re.findall(pattern, await page.text())[1]

        headers_ws = {
                'Upgrade': 'websocket',
                'Origin': 'https://c.kuku.lu',
                'Cache-Control': 'no-cache',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                'Pragma': 'no-cache',
                'Connection': 'Upgrade',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
                'Sec-WebSocket-Version': '13',
                'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
                'Sec-WebSocket-Key': self.sec_websocket_key,
            }

        try:
            async with self.session.ws_connect('wss://ws-c.kuku.lu:21001/', headers=headers_ws) as ws:
                print('ログインを試みています・・')

                join_json = json.dumps({
                    "type": "join",
                    "room": room,
                    "cookie_token": self.cookie_token,
                    "name": "ああああ#1030"
                })

                await ws.send_str('@' + join_json)

                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            m = json.loads(msg.data.removeprefix("@"))
                        except Exception as e:
                            print(f"JSONデコードエラー: {e}")
                            continue

                        match m.get('type'):
                            case "join_complete":
                                self.room_id = m.get('room')
                                self.user_id = m.get('user')
                                await self.dispatch('on_ready')
                            case "data":
                                from ChaatPy.chaatpy import Message
                                await self.dispatch('on_message', Message(m.get('data')))
                            case "polling":
                                if not self.user_id:
                                    print("警告: user_id が未設定です。pollingスキップ。")
                                    continue
                                if self.user_id == m.get('user'):
                                    await ws.send_str('@' + json.dumps({"type": "polling"}))
                            case _:
                                continue
                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        print("WebSocket 接続が切断されました。再接続を試みます。")
                        await asyncio.sleep(2)
                        await self.join(room)
                        return
        except aiohttp.ClientError as e:
            print(f"接続エラー: {e}")
            await asyncio.sleep(3)
            await self.join(room)