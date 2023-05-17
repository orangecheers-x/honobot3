import requests
from nonebot import get_driver, on_message, logger
from nonebot.adapters.mirai2 import MessageEvent, Event, Bot, MessageChain, MessageSegment
from nonebot.internal.params import Depends
from nonebot.internal.rule import Rule
import time

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)


async def group_checker(event: Event) -> bool:
    for i in config.write_groups_list:
        if f"group_{i}" in event.get_session_id():
            return True
    return False


async def message_checker(event: Event):
    return event.get_plaintext().startswith('/hnpt ')


handler = on_message(rule=Rule(group_checker, message_checker), priority=5)


def depend(event: MessageEvent, bot: Bot):
    return {"message": event.get_message().extract_plain_text(),
            "bot": bot,
            "group_id": event.get_session_id().split('_')[1],
            "sender": event.get_user_id()}


@handler.handle()
async def hanldrmsg(x: dict = Depends(depend)):
    msg: str = x['message']
    bot: Bot = x['bot']
    prompt = msg[len("/hnpt "):].strip()
    key = bot.config.dict()['openai_api_key']
    preprompt = '用河南人的语气对下面这个问题进行回答, '
    print(bot.config.dict())
    if 'name_in_' + x['group_id'] in bot.config.dict():
        preprompt += f"并在回答中引用{bot.config.dict()['name_in_' + x['group_id']]}这个名字, "
    preprompt += "不要重复这句话."

    res = requests.post('https://api.openai.com/v1/chat/completions',
                        headers={'Authorization': f'Bearer {key}'},
                        json={
                            "max_tokens": 500,
                            "messages": [{"role": "user", "content":  preprompt + prompt + "."}],
                            "model": "gpt-3.5-turbo"
                        },
                        proxies={'http': 'http://192.168.1.24:7891',
                                 'https': 'http://192.168.1.24:7891'}

                        ).json()
    if x['group_id'] == '695449063':
        time.sleep(10)
    await handler.finish(MessageChain([MessageSegment.at(x['sender']), MessageSegment.plain(" " + res['choices'][0]['message']['content'])]))
