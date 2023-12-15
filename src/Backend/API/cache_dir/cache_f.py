from flask import Flask
from flask_caching import Cache

from src.Backend.API.app_f import app

# 配置缓存
cache_config = {
    "DEBUG": True,          # 是否开启调试模式
    "CACHE_TYPE": "simple", # 使用简单缓存类型，您可以根据需要选择不同的缓存类型
    "CACHE_DEFAULT_TIMEOUT": 86400 # 设置默认缓存时间为1天（86400秒）
}

app.config.from_mapping(cache_config)

cache = Cache(app)
