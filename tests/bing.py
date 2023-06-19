import asyncio
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle


async def main():
    bot = await Chatbot.create()
    print(await bot.ask(prompt="Hello world", conversation_style=ConversationStyle.creative))
    await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
