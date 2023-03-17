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
        'role': 'system', 'content': f'''
        请扮演一名网站编辑，并根据以下要求评估新闻内容：
        1、提炼新闻关键词。
        2、判断新闻内容是否与“今日热搜”相关。
        3、使用以下指标对新闻进行评分(分值范围1-5分):
            a. 时效性：衡量新闻内容的紧迫性和新颖性，反映新闻对读者的实时性和吸引力。
            b. 新闻价值：评估新闻事件的新鲜度、独特性和引人瞩目程度。
            c. 实用性：衡量新闻内容对读者的实际应用价值，如提供有益的见解或解决方案。
            d. 客观性：衡量新闻内容在陈述事实和观点时的公正和中立程度，避免主观或情绪化的语言。
            e. 受众广泛性：评估新闻内容对不同受众的吸引力，包括地域、年龄、职业和兴趣等方面。
            f. 多元视角：考虑报道是否涵盖不同的观点，避免单一价值取向。
            g. 公益性：评估新闻内容是否基于公共利益，而非过度宣传特定产品、服务或品牌。
            h. 娱乐性：衡量新闻内容在吸引读者兴趣、引发情感反应和提供轻松愉快的阅读体验方面的表现。
            i. 流行度:根据与“今日热搜”的关联程度为新闻加分，相关新闻可加1-5分，无关新闻不加分。

        今日热搜:{hotwords.aggre()}

        请按照以下格式回复:
        关键词: aaa\tbbb\tccc
        热搜: 是|否
        时效性: x分\t新闻价值: x分\t实用性: x分\t客观性: x分\t受众广泛性: x分\t多元视角: x分\t公益性: x分\t娱乐性: x分\t流行度: x分
        总分: y分
        评价理由: zzzzzzz
        '''}]


if __name__ == "__main__":
    print(config.conversation[0]['content'])
