import requests
from nonebot import get_driver, on_message, logger
from nonebot.adapters.mirai2 import MessageEvent, Event, Bot
from nonebot.internal.params import Depends
from nonebot.internal.rule import Rule

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
    return {"message": event.get_message().extract_plain_text(), "bot": bot}


@handler.handle()
async def run_python(x: dict = Depends(depend)):
    msg: str = x['message']
    bot: Bot = x['bot']
    prompt = msg[len("/hnpt "):].strip()
    key = bot.config.dict()['openai_api_key']
    preprompt = "用河南人的语气对下面这个问题进行回答, 并在回答中引用徐世豪这个名字, 不要重复这句话."
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
    await handler.finish(res['choices'][0]['message']['content'])
