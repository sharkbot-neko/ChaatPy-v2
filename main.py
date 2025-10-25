import asyncio
import os

import orjson
from ChaatPy import chaatpy
import aiohttp
import dotenv

dotenv.load_dotenv()

async def main():
    client = chaatpy.Client(prefix='?', debug=False)
    await client.create_session()
    await client.getCSTFToken()

    channel = client.getChannel(os.environ.get('HASHID'))

    @client.event
    async def on_ready():
        print('キャッシュしました。')
        print("[on_ready] 起動完了")

    @client.event
    async def on_message(message: chaatpy.Message):
        if message is None:
            return

        print(f"[on_message] [{message.name}] {message.msg}")
        await client.process_command(message)

    @client.command("test")
    async def test_command(message: chaatpy.Message, *args):
        await channel.send(chaatpy.Message({'type': 'chat', 'msg': 'Test Now.'}))
        return 
    
    @client.command("cat")
    async def cat_command(message: chaatpy.Message, *args):
        async with client.session.get(
            "https://api.thecatapi.com/v1/images/search?size=med&mime_types=jpg&format=json&has_breeds=true&order=RANDOM&page=0&limit=1"
        ) as cat:
            await channel.send(chaatpy.Message({'type': 'chat', 'msg': orjson.loads(await cat.text())[0]["url"]}))

    try:
        await client.join(channel.hash)
    except KeyboardInterrupt:
        print("手動で終了しました。")
    finally:
        await client.session.close()


if __name__ == "__main__":
    asyncio.run(main())