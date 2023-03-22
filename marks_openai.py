#!python
import time
import openai
import logging
import requests
from datetime import datetime

from setting import config
from output import Excel
from chrome import CMS

# 日志配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')


class Marks():
    def __init__(self):
        self.keys = config.keys
        openai.api_key = self.keys.pop(0)

        self.excel = Excel()
        # 先读取temp中的excel数据
        self.data = self.excel.read_temp()

    def getRate(self, items):
        error = 0
        results = []
        urls = [i['url'] for i in self.data]

        conversation = config.conversation
        print(conversation[0]['content'])

        # 循环遍历标题数组
        for item in items:

            if item['url'] and item['imgurl'] and item['title'] and item['intro'] and len(item['intro']) > 50:
                if item['url'] in urls:  # 判断url是否存在于self.data中
                    print(f'临时文件中已存在{item["title"]}\n')
                    continue

                title = item['title']
                intro = item['intro']

                # 重命from名字段后保存
                source_from = item.pop('from')
                item["source_from"] = source_from

                conversation = conversation[:1]
                conversation.append({
                    'role': 'user',
                    'content': f'新闻标题:{title}\n新闻介绍:{intro}\n新闻来源:{source_from}'
                })

                # 调用 getResult() 方法获取 ChatGPT 返回的结果，等待其返回
                completion = self.getResult(conversation)
                if not completion:
                    error += 1
                    if error > 5:
                        logging.exception('API key 错误')
                        return results
                    else:
                        continue

                item['evaluate'] = completion
                print(title, '\n', completion, '\n')

                # 转换时间格式
                dt = datetime.fromtimestamp(item['pubtime'])
                item["published_at"] = dt.strftime("%Y-%m-%d %H:%M:%S")

                # 抽取completion信息
                res = self.excel.extract(completion)
                if res:
                    for label, value in res.items():
                        item[label] = value

                results.append(item)
                time.sleep(3)

        # 返回打分结果
        return results

    # 根据内容获取评分结果

    def getResult(self, prompt):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=prompt,  temperature=0.1)
            # 获取结果字符串
            text = completion.choices[0].message.content.strip()

            # 返回评分结果
            return text

        except Exception as e:
            logging.exception(e)
            # 切换 API 密钥
            if self.keys:
                openai.api_key = self.keys.pop(0)
            else:
                logging.exception('No API key available!')
            return None

    # 主函数
    def main(self):
        for api in config.apis:
            try:
                # 发送 API 请求并获取 JSON 响应
                response = requests.get(api)
            except Exception as e:
                logging.exception(e)
                continue

            # 将响应解析为JSON格式，并取出items中的前xx个元素
            items = response.json()['items'][:32]

            # 获取评分结果
            result = self.getRate(items)

            if result:
                # 备份临时数据
                self.data.extend(result)
                self.excel.save('temp', self.data)

        if self.data and len(self.data) >= 12:

            # 更新CMS
            CMS(self.data).update()

        else:
            logging.exception('There are no sufficient news to update!')


if __name__ == "__main__":
    Marks().main()
