from nonebot import get_driver, on_message, on_command, logger
from nonebot.adapters.mirai2 import Bot, MessageSegment, FriendMessage, Event, MessageChain
from nonebot.internal.rule import Rule

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)


async def user_checker(bot: Bot, event: Event):
    return event.get_user_id() == str(bot.config.dict()['superuser'])

async def message_checker(event: Event):
    s = event.get_plaintext().split()
    return len(s) >= 3 and s[0] == '/sendGroup' and s[1].isdigit()

async def send_friend_checker(event: Event):
    s = event.get_plaintext().split()
    return len(s) >= 3 and s[0] == '/sendFriend' and s[1].isdigit()

async def send_temp_friend_checker(event: Event):
    s = event.get_plaintext().split()
    return len(s) >= 4 and s[0] == '/sendTemp' and s[1].isdigit() and s[2].isdigit()

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

msging = on_message(rule=Rule(user_checker, message_checker))
send_friend = on_message(rule=Rule(user_checker, send_friend_checker))
send_temp_friend = on_message(rule=Rule(user_checker, send_temp_friend_checker))

@msging.handle()
async def _(bot: Bot, event: Event):
    logger.info("send triggered")
    s = event.get_plaintext().split()
    await bot.send_group_message(target=int(s[1]), message_chain=MessageChain(s[2]), quote=None)
    await msging.finish()

@send_friend.handle()
async def _ (bot: Bot, event: Event):
    logger.info("send triggered")
    s = event.get_plaintext().split()
    await bot.send_friend_message(target=int(s[1]), message_chain=MessageChain(s[2]), quote=None)
    await send_friend.finish()

@send_temp_friend.handle()
async def _ (bot: Bot, event: Event):
    logger.info("send triggered")
    s = event.get_plaintext().split()
    await bot.send_temp_message(group=int(s[1]), qq=int(s[2]), message_chain=MessageChain(s[3]), quote=None)
    await send_temp_friend.finish()