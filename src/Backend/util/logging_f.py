from functools import wraps
from flask import request
import json

import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime

# 创建日志目录
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 配置日志文件的名称格式
log_file = os.path.join(log_directory, datetime.now().strftime("%Y%m%d.log"))

# 创建一个日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个handler，用于写入日志文件，每天创建一个新文件
handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=3650)
handler.suffix = "%Y%m%d.log"

# 设置日志记录格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 将handler添加到logger中
logger.addHandler(handler)


def log_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        p = request.path
        uname = ""
        ip = ""
        strategy = ""

        try:
            uname = p.split("/")[-2]
        except:
            pass

        # 处理 POST 请求中的 JSON 数据
        if request.method == 'POST' and request.json:
            js = request.json
            strategy = js.get("strategy", "")
            logger.info(f"Body: {json.dumps(js)}")

        # 处理 GET 请求中的查询参数
        if request.method == 'GET':
            rargs = request.args
            strategy = rargs.get("strategy", "app")
            logger.info(f"Query Params: {rargs}")

        # 获取请求的 IP 地址
        if request.headers:
            rh = request.headers            
            ip = rh.get("Cf-Connecting-Ip", "")

        logger.info(f"\n \n{ip = }, {uname = }, {strategy=}")
        logger.info(f"Path: {p}")
        logger.info(f"Method: {request.method}")

        # 调用原始函数
        response = func(*args, **kwargs)
        return response

    return wrapper