# -*- coding: utf-8 -*-

import requests
import json

# 获取今日热搜，包含抖音、百度


class headline:
    def __init__(self):
        self.keywords = []

    def douyin(self):

        response = requests.get(
            '')

        # 将响应解析为JSON格式，并取出items中的前10个元素
        json_data = json.loads(response.content.decode('utf-8'))
        items = json_data['head_line'][:20]

        for item in items:
            self.keywords.append(item['title'])
        return ', '.join(self.keywords)

    def baidu(self):
        response = requests.get(
            '')
        # 将响应解析为JSON格式，并取出items中的前10个元素
        json_data = json.loads(response.content.decode('utf-8'))
        items = json_data['data']['data']
        for item in items:
            self.keywords.append(item['title'])
        return ', '.join(self.keywords)

    def aggre(self):
        return self.douyin() + ', ' + self.baidu()

# 新闻质量评分，参数配置


class config:
    path = ""

    # cms部分
    url = ""
    email = ""
    password = ""
    execute_url = ''

    apis = []

    # chatgpt部分
    key = ''
    hotwords = headline()
    conversation = [{
        'role': 'system', 'content': f''}]


if __name__ == "__main__":
    print(config.conversation[0]['content'])
