import requests
from nonebot import get_driver, on_message, logger
from nonebot.adapters.mirai2 import MessageEvent, Event, Bot, MessageChain
from nonebot.internal.params import Depends
from nonebot.internal.rule import Rule
import leancloud
import datetime
import thulac
from typing import *
from nonebot import require


from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)
driver = get_driver()


async def group_checker(event: Event) -> bool:
    for i in config.write_groups_list:
        if f"group_{i}" in event.get_session_id():
            return True
    return False


handler = on_message(rule=Rule(group_checker), priority=5)


def depend(event: MessageEvent):
    return {"message": event.get_message().extract_plain_text(),
            "group": event.get_session_id().split('_')[1],
            "sender": event.get_user_id()
            }


@handler.handle()
async def save_message(x: dict = Depends(depend)):
    msg: str = x['message']
    Msg = leancloud.Object.extend('message')
    messageObject = Msg()
    messageObject.set('content', msg)
    messageObject.set('group', x['group'])
    messageObject.set('sender', x['sender'])
    messageObject.save()


async def list_checker(event: Event) -> bool:
    s = event.get_plaintext()
    return s.startswith('/wordlist')
listhandler = on_message(rule=Rule(group_checker, list_checker), priority=5)


async def get_wordlist(group_id: str, bot: Bot):
    thu1 = thulac.thulac(seg_only=True, filt=True)
    # 查询今天所有的信息放入一个元素为(sender, content)的字典中
    query = leancloud.Query('message')
    query.equal_to('group', group_id)
    query.greater_than_or_equal_to('createdAt', datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0))
    query.ascending('createdAt')
    query.limit(1000)
    messages = query.find()
    msg: Dict[str, Dict[str, Union[Dict[str, int], int]]] = {}
    if len(messages) == 0:
        await listhandler.finish("今天还没有人说话呢")
    # print(messages[0].get('content'))
    for message in messages:
        sender = message.get('sender')
        content = message.get('content')
        res_list = thu1.cut(content)
        # print(res_list)
        for i in res_list:
            i = i[0]
            if len(i) < 2:
                continue
            if i in msg:
                msg[i]['sum'] += 1
                if sender in msg[i]['sender']:
                    msg[i]['sender'][sender] += 1
                else:
                    msg[i]['sender'][sender] = 1
            else:
                msg[i] = {'sum': 1, 'sender': {sender: 1}}
    # print(msg)
    # 按照sum排序
    msg = sorted(msg.items(), key=lambda x: x[1]['sum'], reverse=True)
    # 按照sender排序
    for i in msg:
        i[1]['sender'] = sorted(
            i[1]['sender'].items(), key=lambda x: x[1], reverse=True)
    result = "今天的高频词汇Top10:\n"

    async def get_group_memeber_name(qqid):
        memberlist = (await bot.member_list(target=group_id))['data']
        # print(qqid, memberlist)
        filtered = filter(lambda x: str(x['id']) == str(qqid), memberlist)
        return list(filtered)[0]['memberName']
    for i in msg[:10]:
        result += f"{i[0]}: {i[1]['sum']}\n"
        for j in i[1]['sender'][:3]:
            result += f"    {await get_group_memeber_name(j[0])}: {j[1]}\n"
    return result


@listhandler.handle()
async def wordlist(event: MessageEvent, bot: Bot):
    # print()
    await handler.send("处理中, 请稍等")
    group_id = event.get_session_id().split('_')[1]
    result = await get_wordlist(group_id=group_id, bot=bot)
    await listhandler.finish(result)

scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", month='*', day='*', hour="23", minute="59", second="0")
async def run_every_4():
    bot = driver.bots[driver.config.dict()['mirai_qq'][0]]
    for group_id in config.write_groups_list:
        result = await get_wordlist(group_id=group_id, bot=bot)
        result = "一天结束啦\n" + result
        await bot.send_group_message(target=group_id, message_chain=MessageChain(result))
