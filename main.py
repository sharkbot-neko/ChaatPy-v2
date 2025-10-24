import asyncio
from ChaatPy import chaatpy


async def main():
    client = chaatpy.Client()
    await client.create_session()
    await client.getCSTFToken()

    @client.event
    async def on_ready():
        print("起動完了")

    @client.event
    async def on_message(message: chaatpy.Message):
        print(f"[{message.name}] {message.msg}")
        if message.msg == 'こんにちは':
            await channel.send(chaatpy.Message({'msg': 'こんにちは！！', 'type': 'chat'}))

    channel = client.getChannel('ChannelID')

    try:
        await client.join(channel.hash)
    except KeyboardInterrupt:
        print("手動で終了しました。")
    finally:
        await client.session.close()


if __name__ == "__main__":
    asyncio.run(main())