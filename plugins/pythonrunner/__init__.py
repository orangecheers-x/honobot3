import requests
from nonebot import get_driver, on_message, logger
from nonebot.adapters.mirai2 import MessageEvent, Event
from nonebot.internal.params import Depends
from nonebot.internal.rule import Rule

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass


# write_groups_list = ['776324219']

async def group_checker(event: Event) -> bool:
    for i in config.write_groups_list:
        if f"group_{i}" in event.get_session_id():
            return True
    return False


async def message_checker(event: Event):
    return event.get_plaintext().startswith('+++py')


handler = on_message(rule=Rule(group_checker, message_checker), priority=5)


def depend(event: MessageEvent):
    return {"message": event.get_message().extract_plain_text()}


@handler.handle()
async def run_python(x: dict = Depends(depend)):
    msg: str = x['message']
    code = msg[len("+++py"):].strip()
    header = {
        'Host': 'tool.runoob.com',
        'Referer': 'https://www.runoob.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    sess = requests.session()
    res = sess.get(
        "https://www.runoob.com/try/runcode.php?filename=helloworld&type=cpp")
    token = res.text.split('token = \'')[1].split("'")[0]
    submiturl = 'https://tool.runoob.com/compile2.php'
    data = {
        'code': code,
        'token': token,
        'language': 15,
        'fileext': 'py3',
        'stdin': input
    }
    res = sess.post(submiturl, headers=header, data=data)
    output = res.json()['output']
    err = res.json()['errors']
    logger.warning(code)
    logger.warning("output: "+output)
    logger.warning("error: " + err)
    if err.strip() != "":
        await handler.finish(err)
    else:
        await handler.finish(output)
