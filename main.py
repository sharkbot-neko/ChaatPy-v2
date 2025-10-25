import asyncio
import os
from ChaatPy import chaatpy
import logging
import dotenv

dotenv.load_dotenv()

async def main():
    client = chaatpy.Client(prefix='?')
    await client.create_session()
    await client.getCSTFToken()

    channel = client.getChannel(os.environ.get('HASHID'))

    @client.event
    async def on_ready():
        print('キャッシュしました。')
        print("[on_ready] 起動完了")

    @client.event
    async def on_message(message: chaatpy.Message):
        print(f"[on_message] [{message.name}] {message.msg}")
        await client.process_command(message)

    @client.command("test")
    async def test_command(message: chaatpy.Message, *args):
        await channel.send(chaatpy.Message({'type': 'chat', 'msg': 'Test Now.'}))
        return 

    try:
        await client.join(channel.hash)
    except KeyboardInterrupt:
        print("手動で終了しました。")
    finally:
        await client.session.close()


if __name__ == "__main__":
    asyncio.run(main())