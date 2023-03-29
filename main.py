import requests
import logging
from setting import config

# 通过api获取全部数据,并初步处理
class Data():
    def __init__(self):
        self.data = self.get_all_data()

    # 通过api获取全部数据
    def get_all_data(self):
        data = []

        for api in config.apis:
            try:
                # 发送 API 请求并获取 JSON 响应
                response = requests.get(api)
            except Exception as e:
                logging.info('Get data failed!\n')
                logging.exception(e)
                continue

            # 将响应解析为JSON格式
            items = response.json()['items']
            logging.info(f'Get {len(items)} items from {api}.\n')
        
        data.append(items)
        logging.info(f'Get {len(data)} items from all apis.\n')
        return data

    # 获取data中的title字段，拼接成list，结构为 ["0. title0" \n1. title2"]
    def get_titles(self):
        titles = ''
        for i in range(len(self.data)):
            titles += f'{i}. {self.data[i]["title"]}\n'
        return titles

