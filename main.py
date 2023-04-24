
import os
import re
import json
import time
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
        old_data = Excel.read_data('data/api')
        # 从api中获取数据
        new_data = API.get_news()
        # 合并数据
        raw_data = Excel.merge(old_data, new_data)
        # 筛选出24小时内的数据
        for item in raw_data:
            ptm = Excel.time_gap(item['pubtime'])
            if ptm < 1:
                self.data.append(item)
        # 为每条数据添加编号
        lens = len(self.data)
        for i in range(lens):
            self.data[i]['no'] = i
        # 备份api数据
        # Data.backup(self.data)
        Excel.save('temp_api', self.data)

        self.conversation = Data.get_conversation()

    @staticmethod
    def get_conversation():

        prompt1 = '''
        请扮演一名具有ChatGPT4能力的网站编辑，帮我筛选8条不同主题、最有吸引力的新闻，请优先选择与[热门话题]相关的新闻。
        
        思考步骤：
        1、重新排序，与[热门话题]相关的新闻排在最前。
        1、根据新闻标题判断它们所涉及的主题。主题参考：
        俱乐部新闻、转会市场、足球联赛、中国足协、奥运会、世界杯、冠军杯、亚洲杯、国内篮球联赛、NBA赛事、青少年赛事、网球赛事、社会热点、犯罪案件、反腐打黑、食品安全、交通事故、自然灾害、时尚穿搭、美食旅行、文化艺术、科技新品发布、产品评测、人工智能、芯片科技、娱乐圈绯闻、明星家庭、两性关系、婚姻生活、电影票房、影视剧评论、电影节...
        2、 相同主题只保留一条最有吸引力的新闻，优先选择与[热门话题]相关的新闻。
        
        回复格式：
        请按以上步骤思考后，json格式返回8个不同主题及其新闻编号：
        [{"no":<编号1>,"field":<主题1>},
        {"no":<编号2>,"field":<主题2>}]
        
        注意：
        1、field字段的主题不要重复，与[热门话题]相关的主题排在最前。
        2、请勿更改新闻编号，不要解释，不要添加任何多余字符。

        热门话题：
        '''

        prompt2 = '''
        Please play the role of a website editor with ChatGPT4 capabilities and help me select the top 8 most attractive news articles. Please prioritize news related to [Hot Topics]. Requirements:

        1、Determine the topics involved in each news article based on its title. Topics reference: 
        俱乐部新闻、转会市场、足球联赛、中国足协、奥运会、世界杯、冠军杯、亚洲杯、国内篮球联赛、NBA赛事、青少年赛事、网球赛事、社会热点、犯罪案件、反腐打黑、食品安全、交通事故、自然灾害、时尚穿搭、美食旅行、文化艺术、科技新品发布、产品评测、人工智能、芯片科技、娱乐圈绯闻、明星家庭、两性关系、婚姻生活、电影票房、影视剧评论、电影节...

        2、Select news related to the same topic: only keep the most attractive news article for each topic, prioritizing news related to [Hot Topics].

        3、Please carefully consider and return 8 different topics and their news numbers in json format: 
        [{"no":,"field":}, 
        {"no":,"field":}] 
        Note: The topic in the field field should not be repeated. Please do not change the news numbers, do not explain, and do not add any extra characters.

        Hot Topics:
        '''

        cs = [{
            'role': 'system', 'content': prompt1 + API.aggre()}]
        # logging.info(cs[0]['content'])
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
            return
        logging.info(f'Get sort results:\n{completion}')
        return completion

    # 从排序结果中获取json数据
    def get_json(self, items):
        result = []
        completion = self.get_short(items)
        if not completion:
            return
        try:
            # 将返回结果转成json格式
            result = json.loads(completion)
            logging.info(f'Get {len(result)} items from openai api.\n')
        except Exception as e:
            logging.exception('返回格式有误，通过正则进行匹配：\n')
            # 返回json格式的数据
            res = re.findall(r'\{.*?\}', completion, re.DOTALL)
            if res:
                try:
                    result = json.loads('[' + ','.join(res) + ']')
                    logging.info(f'Get {len(result)} items from openai api.\n')
                    logging.info('拼接json格式成功!\n')
                except:
                    logging.exception('拼接json格式失败!\n')
            else:
                logging.exception('正则表达式匹配失败!\n')
        # 如果是字符串，需要转成int
        for item in result:
            # 判断 item 是否是字典类型，且包含'no'键和值为字符串类型
            if isinstance(item, dict) and 'no' in item:
                item['no'] = int(item['no'])
            else:
                # 如果不满足上述条件，将 no 变量设置为 None，表示无效值
                result.remove(item)
                logging.info(f'Remove item:{item}\n')
        # logging.info(f'Get json data:{result}\n')
        return result[:12]

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
            print(f'There remain {len(data)} items for selection.')
            if len(data) <= 100:
                break

            # 每次从data中取若干条数据,组成items
            items = data[-config.api_content_number:]
            data = data[:-config.api_content_number]
            # 从openai api获取排序结果
            result = self.get_json(items)
            if not result:
                errors += 1
                if errors >= 3:
                    logging.exception('连续3次获取排序结果失败!\n')
                    break
                continue

            # 初始化一个空的dataframe
            news_df = pd.DataFrame(columns=df.columns)
            # 保存排序结果
            for item in result:
                # 在df中查找id对应的数据
                # 处理格式为json的数据
                df_item = df[df['no'] == item['no']].copy()
                # 如果item存在field字段，将field字段插入到df_item中
                if 'field' in item:
                    # df_item['field'] = item['field']
                    df_item.loc[:, 'field'] = item['field']
                # 将df_item插入到new_df中
                news_df = pd.concat([news_df, df_item], ignore_index=True)

                # 校验no和title是否匹配
                # id = item['no']
                # title = item['title']
                # assert self.data[id]['title'] == title
            # 将news_df转成list，插入到data中
            news = news_df.to_dict('records')
            data = news + data

            # 将筛选结果保存到data\api中
            logging.info(f'Save {len(data)} items to data/api.\n')
            Excel.save('data/api', data, False)
            # 避免openai api频繁调用
            time.sleep(config.waiting_time)

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
