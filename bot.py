#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.mirai2 import Adapter as MIRAI2Adapter
import pathlib

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(MIRAI2Adapter)

# 在这里加载插件
nonebot.load_builtin_plugins("echo")  # 内置插件
# nonebot.load_plugin("thirdparty_plugin")  # 第三方插件
nonebot.load_plugin(pathlib.Path("plugins/gpt"))
nonebot.load_plugin(pathlib.Path("plugins/pythonrunner"))
nonebot.load_plugin(pathlib.Path("plugins/send"))

if __name__ == "__main__":
    nonebot.run()
