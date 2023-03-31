
import os
import re
import json
import time
import random
import logging
import pandas as pd

from setting import config
from output import Excel
from apis import API
from marks_openai import Marks

# 通过api获取全部数据,并初步处理


class Data:
    def __init__(self):
        self.data = []
        # 从excel中获取数据
        old_data = Excel.read_temp('temp_api')
        # 从api中获取数据
        new_data = API.get_news(100)
        # 合并数据
        raw_data = Excel.merge(old_data, new_data)
        # 筛选出24小时内的数据
        for item in raw_data:
            ptm = Excel.time_gap(item['pubtime'])
            if ptm <= 24:
                self.data.append(item)
        # 为每条数据添加编号
        lens = len(self.data)
        for i in range(lens):
            self.data[i]['no'] = i
        # 对self.data进行随机排序
        random.shuffle(self.data)
        self.conversation = Data.get_conversation()

    @staticmethod
    def get_conversation():
        cs = [{
            'role': 'system', 'content': '''
    我请你扮演一名网站编辑，帮助我完成：
    1、筛选出12条具有吸引力且涉及不同话题的新闻。
    2、每个主题仅选择一条新闻，避免包含重复或相似主题。
    3、按照话题热度进行排序，与今日热搜相关的话题位置靠前。
    4、返回新闻标题列表，格式如下：
    [{"no": 编号1, "title": "新闻标题1"},
    {"no": 编号2, "title": "新闻标题2"}]

    注意：请返回满足格式要求的JSON格式。不要解释，不要改变新闻编号，不要添加任何多余字符。

    今日热搜：
        ''' + API.aggre()}]
        logging.info(cs[0]['content'])
        return cs

    # 获取data中的title字段，拼接成list，结构为 ["0. title0" \n1. title2"]
    @staticmethod
    def get_titles(items):
        titles = ''
        logging.info(f'Read {len(items)} titles, to a get question.')
        for item in items:
            if 'title' in item:
                titles += f'{item["no"]}. {item["title"]}\n'
            else:
                logging.info(f'No title in {item}')
        logging.info(f'Sort these news:\n{titles}')
        return titles

    # 将data数据发送给openAI api获取排序结果
    def get_short(self, items):
        cs = self.conversation.copy()
        titles = Data.get_titles(items)
        cs.append({
            'role': 'user',
            'content': titles
        })
        completion = API.get_result(cs)
        if not completion:
            logging.exception('返回结果为空!\n')
            return completion
        logging.info(f'Get sort results:\n{completion}')
        return completion

    # 从排序结果中获取json数据
    def get_json(self, items):
        result = []
        completion = self.get_short(items)
        if not completion:
            return result
        try:
            # 将返回结果转成json格式
            result = json.loads(completion)
            logging.info(f'Get {len(result)} items from openai api.\n')
        except Exception as e:
            logging.exception('返回json格式有误!\n')
            # 使用正则表达式，匹配排序结果中所有{}中间的内容,不包括{}
            res = re.findall(r'\{.*?\}', completion, re.DOTALL)
            if res:
                try:
                    result = json.loads('[' + ','.join(res) + ']')
                    logging.info(f'Get {len(result)} items from openai api.\n')
                except Exception as e:
                    logging.exception('拼接json格式失败!\n')
            else:
                logging.exception('正则表达式匹配失败!\n')
        # result的'no'字段如果是字符串，需要转成int
        for item in result:
            if isinstance(item['no'], str):
                item['no'] = int(item['no'])
        return result[:16]

    # 更新本地数据
    @staticmethod
    def backup(items):
        # 备份临时数据
        Excel.remove_temp('temp_api')
        Excel.save('temp_api', items)

    # 从openai api获得排序结果
    def main(self):
        errors = 0
        # 复制一份self.data，避免对self.data进行修改
        data = self.data.copy()
        df = pd.DataFrame.from_records(self.data)

        while True:
            print(
                f'There remain {len(data)} items for selection.')
            if len(data) < 120:
                break

            # 每次从data中取36条数据,组成items
            items = data[:36]
            data = data[36:]
            # 从openai api获取排序结果
            results = self.get_json(items)
            if not results:
                errors += 1
                if errors > 3:
                    logging.exception('连续3次获取排序结果失败!\n')
                    break
                continue

            # 初始化一个空的dataframe
            news_df = pd.DataFrame(columns=df.columns)
            # 保存排序结果
            for item in results:
                # 在df中查找id对应的数据
                df_item = df[df['no'] == item['no']]
                # 将df_item插入到new_df中
                news_df = pd.concat([news_df, df_item], ignore_index=True)

                # 校验no和title是否匹配
                # id = item['no']
                # title = item['title']
                # assert self.data[id]['title'] == title
            # 将news_df转成list，插入到data中
            news = news_df.to_dict('records')
            data = data + news

            # 将筛选结果保存到data/api中
            logging.info(f'Save {len(data)} items to data/api.\n')
            Excel.save('data/api', data, False)
            # 休眠6秒，避免openai api频繁调用
            time.sleep(6)

        # 更新本地api数据
        Data.backup(data)
        # 对筛选的新闻进行打分
        mark = Marks(data)
        mark.main()


if __name__ == "__main__":
    # 日志配置
    times = int(time.time())
    log_path = os.path.join(config.folder, 'log', f'main_{times}.log')
    print(f'Log path: {log_path}')

    logging.basicConfig(
        level=logging.INFO,
        filename=log_path,
        filemode='w',
        format='%(asctime)s - %(levelname)s: %(message)s',
        encoding='utf-8')
    logging.info(f'Start running...')

    d = Data()
    d.main()
