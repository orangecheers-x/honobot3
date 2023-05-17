from sys import stderr
import nonebot
from nonebot.adapters import Message, Event
from nonebot import get_driver, on_command
from nonebot.rule import to_me, Rule
from nonebot.matcher import Matcher
from nonebot.params import Arg, CommandArg, ArgPlainText
from nonebot import require
import leancloud

from .config import Config

from nonebot.log import logger, default_format

driver = get_driver()
global_config = driver.config


# print(global_config)
# config = Config.parse_obj(global_config)

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

def acmrule():
    async def _checker(event: Event) -> bool:
        logger.debug(f"group_{global_config.qqg}")
        return f"group_{global_config.qqg}" in event.get_session_id()

    return Rule(_checker)


adder = on_command("acmadd", rule=acmrule(), priority=5)
lister = on_command("acmlist", rule=acmrule(), priority=5)


@adder.handle()
async def add(matcher: Matcher, args: Message = CommandArg()):
    params = args.extract_plain_text()
    if params:
        matcher.set_arg('incscore', args)
    pass


@adder.got('incscore', prompt="多少分的题")
async def handle_incscore(event: Event, incstr: str = ArgPlainText('incscore')):
    inc = 0
    try:
        inc = int(incstr)
    except:
        await adder.finish("输个数字")

    query = leancloud.Query('acm')
    qq = event.get_session_id().split('_')[-1]
    query.equal_to('qq', qq)
    res = query.find()
    obj: leancloud.Object = res[0]
    std = 1400
    if qq == '1322562081':
        std = 400

    if inc < 0:
        await adder.finish("?")
        return
    elif inc < std and std == 1400:
        await adder.finish("太强了🌹, 虽然1400以下不计分.")
        return
    elif inc < std and std == 400:
        await adder.finish("太强啦💗, 虽然400以下不计分.")
        return 
    else:
        obj.increment('score', inc - std)
        obj.save()
        Acmlog = leancloud.Object.extend('acmlog')
        acmlog: leancloud.Object = Acmlog()
        acmlog.set('qq', qq)
        acmlog.set('record', inc)
        acmlog.save()
        s = "可以!"
        if inc == std:
            s = "你好强!"
        if inc >= std+400:
            s = "强!"
        if inc >= std+600:
            s = "太强了!"
        if inc >= std+700:
            s = "nb!"
        if inc >= std+800:
            s = "无敌了!"
        if inc >= std+1100:
            s = "我超, 你好强!"
        if inc >= std+1300:
            s = "太nb了!带我拿金!"
        s += f" 获得了{inc - std}分!"
        if qq == '1322562081':
            s += '💗'
        await adder.finish(s)


@lister.handle()
async def list(matcher: Matcher):
    query = leancloud.Query('acm')
    query.descending('score')
    res = query.find()
    ans = ""
    for i in res:
        obj: leancloud.Object = i
        ans += f"{obj.get('name')} \t {obj.get('score')} \n"
    logger.debug(ans)
    await lister.finish(ans)
    pass


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", month='*', day='*', hour="4", minute="0")
async def run_every_4():
    bot = driver.bots[str(global_config.bot_id)]
    query = leancloud.Query('acm')
    query.descending('score')
    res = query.find()
    ans = "结算时间到! 每人扣除600分:\n"
    for i in res:
        obj: leancloud.Object = i
        obj.increment('score', -600)
        obj.save()
        ans += f"{obj.get('name')} \t {obj.get('score')} \n"
    await bot.send_group_msg(group_id=global_config.qqg, message=ans)
    pass
