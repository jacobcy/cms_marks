# -*- coding: utf-8 -*-


import os
import re
import time
import logging
import pandas as pd
from setting import config


class Excel():
    def __init__(self):
        self.timestamp = int(time.time())
        # 指标名称
        self.columns = ['timeliness', 'news_value', 'practicality', 'objectivity',
                        'wideness', 'diversity', 'entertainment', 'popularity', 'mark']

    # 默认读取test文件夹中的excel文件
    def read(self, file):
        # 读取 Excel 文件
        df = pd.read_excel(file)

        # 转换为 JSON 格式
        items = df.to_dict('records')

        return items

    # 读取temp文件夹中的excel文件
    def read_temp(self):
        data = []

        temp = os.path.join(config.folder, 'temp')
        logging.info('正在读取temp文件夹中的文件')

        if not os.path.exists(temp):
            os.mkdir('temp')
            logging.info('创建temp文件夹')

        else:
            files = os.listdir(temp)
            logging.info(f'读取temp文件夹中的文件: {files}')

            for file in files:
                if file.endswith('.xlsx'):
                    # 读取文件
                    new_data = self.read(
                        os.path.join(config.folder, 'temp', file))
                    # 去重
                    for item in new_data:
                        if item not in data:
                            data.append(item)

            mounts = len(data)
            logging.info(f'已读取temp文件夹中【{mounts}】条数据')
        return data

    # 保存文件
    def save(self, folder, data):

        # 将字典列表直接转换为DataFrame
        df = pd.DataFrame.from_records(data)

        # 生成一个3位的随机数
        random = str(int(time.time()))[-3:]

        excel_path = os.path.join(
            config.folder, folder, f'items_{self.timestamp}_{random}.xlsx')
        logging.info(f"正在保存文件: {excel_path}")

        try:
            df.to_excel(excel_path, index=False)
            return excel_path

        except:
            logging.exception("Failed to save Excel file")

    # 读取excel文件并保存为jsonL格式
    def toJson(self, excel_path):

        # 读取 Excel 文件
        df = pd.read_excel(excel_path)

        # 删除不需要的列
        df = df.drop(columns=['imgurl', 'pubtime',
                     'published_at', 'intro', 'url'])

        # 重新生成指标数据
        # try:
        #     df = df.drop(columns=['keywords', 'hot_related', 'reason'])
        #     df = df.drop(columns=self.columns)
        # except:
        #     pass
        # items = df.to_dict('records')
        # for item in items:
        #     evaluate = item['evaluate']
        #     res = self.extract(evaluate)
        #     if res:
        #         for label, value in res.items():
        #             item[label] = value
        # 将json数据展平
        # df = pd.json_normalize(items)

        df1 = df.drop(columns=['evaluate'])
        trans_columns = ['时效', '新闻', '实用', '客观', '广泛', '多元', '娱乐', '流行', '总分']
        mapping = dict(zip(self.columns, trans_columns))

        # 表头重命名为中文
        try:
            names = mapping
            df1 = df1.rename(columns=names)
        except:
            pass

        # 保存json格式的csv文件，便于查看评分
        json_path = os.path.join(config.folder, 'data',
                                 f'output_{self.timestamp}.csv')
        df1.to_csv(json_path, index=False, encoding='utf-8-sig')

        # 删除多余的列
        try:
            df = df.drop(
                columns=['source_from', 'keywords', 'hot_related', 'reason'])
            df = df.drop(columns=self.columns)
        except:
            pass
        df = df.rename(columns={'title': 'prompt', 'evaluate': 'completion'})

        # 保存为jsonL格式的csv文件，用于上传训练
        jsonL_path = os.path.join(config.folder, 'data',
                                  f'training_data_{self.timestamp}.csv')

        with open(jsonL_path, 'w', encoding='utf-8') as f:
            for index, row in df.iterrows():
                # 将每行数据转换为json格式的字符串
                json_str = row.to_json(force_ascii=False)
                # 写入文件，并添加换行符
                f.write(json_str)
                f.write('\n')

    # 提取评分结果中的指标数据
    def extract(self, text):

        pattern = r"关键词(?P<keywords>.*?)\n.*?热搜.*?(?P<hot_related>是|否).*?理由(?P<reason>[\s\S]*)"

        match = re.search(pattern, text, re.DOTALL)
        result = match.groupdict() if match else {}

        if result and result['keywords']:
            result['keywords'] = re.sub(r'[,，、]', ' ', result['keywords'])
            result['keywords'] = re.sub(
                r'[^\w\s]', '', result['keywords']).strip()

        # 提取理由
        if result and result['reason']:
            # 替换冒号
            result['reason'] = re.sub('[：:]', '', result['reason']).strip()

        # 提取指标数据
        values = {k: v for v, k in enumerate(self.columns)}

        patterns = [
            r"时效性.*?(?P<timeliness>\d)分",
            r"新闻性.*?(?P<news_value>\d)分",
            r"实用性.*?(?P<practicality>\d)分",
            r"客观性.*?(?P<objectivity>\d)分",
            r"广泛性.*?(?P<wideness>\d)分",
            r'多元化.*?(?P<diversity>\d)分',
            r"娱乐性.*?(?P<entertainment>\d)分",
            r'话题度.*?(?P<popularity>\d)分',
            r'总分.*?(?P<mark>\d+)分'
        ]

        for item, value in values.items():
            match = re.search(patterns[value], text)
            result[item] = int(match.group(item)) if match else 0

        return result


if __name__ == "__main__":
    text = '''
        关键词: OPPO    Find X6 全球首发。
        热搜关联性: 否。

        时效性: 4分。新品发布是一个高时效性的事件，而且该新品还未发布，预热期间也受到了关注。
        新闻性: 3分。介绍了一个新品的基本信息，但并没有详细介绍其特点和功能，新闻价值略低。
        实用性: 2分。介绍了一个新品的发布时间，对读者的实际应用价值不高。
        客观性: 5分。该新闻以事实为基础，没有使用主观或情绪化的语言。
        广泛性: 2分。该新闻只涉及一个品牌和一个产品系列，对不同受众的吸引力不高。
        多元化: 1分。该新闻仅介绍了单一产品，没有公益性的视角。
        娱乐性: 2分。该新闻仅介绍了单一产品，没有娱乐性。
        话题度: 2分。该新闻未出现在今日热搜，话题度不高。
        总分: 19分。

        评分理由: 该新闻在时效性方面得分较高，但在新闻性、实用性、广泛性和公益性方面得分较低。虽然客观性方面得分较高，但是该新闻仅仅介绍了单一产品，完全没有公益性的视角，是一篇软性广告。话题度方面得分也不高。综上所述，该新闻总分较低。
    '''
    e = Excel()
    print(e.extract('text'))
