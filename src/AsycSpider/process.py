import pandas as pd
import aiohttp
import asyncio
import time

"""
流程： url -> response -> data -> item 

使用备忘:自定义好数据处理函数f即可使用
f: json/html -> dict 
"""
class Spider:
    def __init__(self, f, data_format="json", headers= {}, max_concurrent = 25) -> None:
        """
            f: raw data 处理函数, 处理后的data 为所需的dict格式,直接用于生成item
        """
        self.max_concurrent = max_concurrent
        self.headers = headers
        self.f = f
        self.data_format = data_format

    async def fetch_item_from_url(self, url, session, semaphore):
        async with semaphore:  # Limit the number of simultaneous requests
            try:
                async with session.get(url, headers = self.headers) as response:
                    if self.data_format == "json":
                        rawdata = await response.json()
                    elif self.data_format == "html":                        
                        html = await response.text()
                        rawdata["html"] = html
                    else:
                        assert False
                    rawdata["url"] = url
            except:
                rawdata = {}    
            data = self.f(rawdata)
            item = Item(data)
            
            return item

    async def collect_data_for_urls(self, urls):
        if len(urls) > 500:
            raise ValueError(f"too many urls one times, max = 500, now {len(urls) = }")
        
        semaphore = asyncio.Semaphore(self.max_concurrent)  # Limit to max_concurrent requests at a time
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_item_from_url(url, session, semaphore) for url in urls]
            return await asyncio.gather(*tasks)

    def run(self, urls):
        items = asyncio.run(self.collect_data_for_urls(urls))
        t = pd.Timestamp(time.time(),unit = "s")
        print(f"finish spider {t=}")
        return items

class Item:
    def __init__(self, data):
        for k, v in data.items():
            setattr(self, k, v)
