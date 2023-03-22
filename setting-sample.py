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

    # cms参数
    url = ""
    email = ""
    password = ""
    execute_url = ''

    apis = []

    # chatgpt部分
    key = ''
    hotwords = headline()
    index = f'时效性: x分\t新闻性: x分\t实用性: x分\t客观性: x分\t广泛性: x分\t多元化: x分\t公益性: x分\t娱乐性: x分\t流行度: x分\t总分: y分'

    conversation = [{
        'role': 'system', 'content': f'''
        请扮演一名网站编辑，评估新闻质量：
        1、提炼新闻关键词。
        2、判断新闻主题是否与“今日热搜”相关。
        3、使用以下指标对新闻进行评分(分值范围1-9分):
            a. 时效性：衡量新闻事件是否紧迫及时。
            b. 新闻性：评估新闻标题是否引人瞩目、吸引眼球。
            c. 实用性：考虑内容对读者的实际价值，如提供有益的见解或解决方案。
            d. 客观性：根据新闻来源，判断内容在陈述事实和观点时是否公正和中立。
            e. 广泛性：评估新闻事件的地域影响范围，全国>(北京、上海)>省>地级市。
            f. 多元化：考虑报道内容是否丰富，而非对单一产品或品牌进行商业性宣传。
            g. 娱乐性：考虑内容在吸引读者兴趣、引发情感反应方面的表现。
            h. 流行度：衡量内容与“今日热搜”的相关性。

        今日热搜:{hotwords.aggre()}

        按照以下格式回复:
        关键词: aaa\tbbb\tccc
        热搜: 是|否
        时效性: x分\t新闻性: x分\t实用性: x分\t客观性: x分\t广泛性: x分\t多元化: x分\t娱乐性: x分\t流行度: x分
        总分: y分
        评价理由: zzzzzzz
        '''}]


if __name__ == "__main__":
    print(config.conversation[0]['content'])
