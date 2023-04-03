import json
import logging
import requests
import openai
from setting import config

# 获取今日热搜，包含抖音、百度
keys = config.keys
openai.api_key = keys.pop(0)


class API:
    def __new__(cls, name, bases, dct):
        # 将类中的所有方法转换为静态方法
        for attr, value in dct.items():
            if callable(value):
                dct[attr] = staticmethod(value)
        return super().__new__(cls, name, bases, dct)

    # 从openai API获取反馈结果
    def get_result(prompt):
        try:
            logging.info('正在获取openai的反馈结果...')
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=prompt,  temperature=0.1)
            # 获取结果字符串
            text = completion.choices[0].message.content.strip()
            # 返回结果
            return text
        except Exception as e:
            logging.info('Here is the error:\n ')
            logging.exception(e)
            # 切换 API 密钥
            if keys:
                openai.api_key = keys.pop(0)
            else:
                logging.exception('No other API key available!')
            return None

    # 通过api获取数据

    def get_news(num=0):
        all_items = []
        for api in config.apis:
            try:
                # 发送 API 请求并获取 JSON 响应
                response = requests.get(api)
            except Exception as e:
                logging.info(f'Get data from {api} failed!')
                logging.exception(e)
                continue
            # 将响应解析为JSON格式
            items = response.json()['items']
            if num:
                items = items[:num]
            logging.info(f'Get {len(items)} items from {api}.')
            all_items.extend(items)
        logging.info(f'Get {len(all_items)} items from all apis.\n')
        # 保存临时数据
        # try:
        #     Excel.save('temp_api', all_items)
        # except Exception as e:
        #     logging.exception(e)
        return all_items

    def douyin():
        json_data = None
        try:
            response = requests.get(
                'https://www.douyin.com/aweme/v1/web/ad/hotspot/?ug_source=hh_rb')

            # 将响应解析为JSON格式
            json_data = json.loads(response.content.decode('utf-8'))
            logging.info('抖音热搜获取成功')
        except:
            logging.info('抖音热搜获取失败')
        items = json_data['head_line'] if json_data else []
        return items

    def baidu():
        json_data = None
        try:
            response = requests.get(
                'https://api2.firefoxchina.cn/homepage/3139.json')
            # 将响应解析为JSON格式
            json_data = json.loads(response.content.decode('utf-8'))
            logging.info('百度热搜获取成功')
        except:
            logging.info('百度热搜获取失败')
        items = json_data['data']['data'] if json_data else []
        return items

    def aggre():
        keywords = []
        items = API.douyin() + API.baidu()
        keywords = [item['title'] for item in items]
        res = ', '.join(keywords)
        logging.info(f'聚合热搜: {res}')
        return res


if __name__ == "__main__":
    print(API.get_news(3))
    print(API.aggre())
