# -*- coding: utf-8 -*-


import os
import re
import time
import shutil
import logging
import pandas as pd
from datetime import datetime
from setting import config


class Excel:
    def __new__(cls, name, bases, dct):
        # 将类中的所有方法转换为静态方法
        for attr, value in dct.items():
            if callable(value):
                dct[attr] = staticmethod(value)
        return super().__new__(cls, name, bases, dct)

    # 时间戳
    timestamp = int(time.time())
    # 指标名称
    columns = ['timing', 'nvalue', 'practical', 'objective',
               'local', 'business', 'joy', 'topic']

    # 读取excel文件并保存为jsonL格式
    def toJson(excel_path):
        if not os.path.exists(excel_path):
            logging.info(f'文件不存在: {excel_path}')
            return
        # 读取 Excel 文件
        df = pd.read_excel(excel_path)
        try:
            # 删除不需要的列
            df = df.drop(columns=['imgurl', 'pubtime',
                                  'published_at', 'intro', 'url'])
        except:
            pass
        # 生成output文件
        df1 = df.drop(columns=['evaluate'])
        # 表头重命名为中文
        trans_columns = ['时效', '价值', '实用', '客观', '地域', '商业', '娱乐', '流行']
        mapping = dict(zip(Excel.columns, trans_columns))
        try:
            df1 = df1.rename(columns=mapping)
        except:
            logging.exception("Failed to rename columns")
        # 保存json格式的csv文件，便于查看评分
        json_path = os.path.join(config.folder, 'data/output',
                                 f'output_{Excel.timestamp}.csv')
        logging.info(f"正在保存文件: {json_path}")
        df1.to_csv(json_path, index=False, encoding='utf-8-sig')
        # 删除多余的列
        try:
            df = df.drop(
                columns=['source_from', 'mark'  # , 'keywords', 'hot_related', 'reason'
                         ])
            df = df.drop(columns=Excel.columns)
        except:
            pass
        # 表头重命名
        df = df.rename(columns={'title': 'prompt', 'evaluate': 'completion'})
        # 保存为jsonL格式的csv文件，用于上传训练
        jsonL_path = os.path.join(config.folder, 'data/train',
                                  f'training_data_{Excel.timestamp}.csv')
        logging.info(f"正在保存文件: {jsonL_path}")
        # 保存为jsonL格式
        with open(jsonL_path, 'w', encoding='utf-8') as f:
            for index, row in df.iterrows():
                # 将每行数据转换为json格式的字符串
                json_str = row.to_json(force_ascii=False)
                # 写入文件，并添加换行符
                f.write(json_str)
                f.write('\n')

    def read_data(path):
        file = os.path.join(config.folder, path, 'items.xlsx')
        if not os.path.exists(file):
            logging.info(f'文件不存在: {file}')
            return {}
        # 读取 Excel 文件
        return Excel.read_xls_to_dict(file)

    # 读取excel文件,并转换为字典列表
    def read_xls_to_dict(file):
        # 判断file是否为绝对路径
        if not os.path.isabs(file):
            file = os.path.join(config.folder, file)
        logging.info(f'正在读取文件: {file}')
        items = []
        # 读取 Excel 文件
        try:
            df = pd.read_excel(file)
        except:
            logging.exception(f'读取文件失败: {file}')
            return items
        # 将nan替换为空字符串，不区分大小写
        df = df.replace(re.compile('nan', re.I), '')
        # 删除有空字段的行
        df = df.dropna(how='any', subset=['url', 'imgurl', 'title'])
        # 根据url列去重
        df = df.drop_duplicates(subset=['url'])
        # 转换为 JSON 格式
        items = df.to_dict('records')
        return items

    # 读取temp文件夹中的excel文件
    def read_temp(folder='temp'):
        data = []
        temp = os.path.join(config.folder, folder)
        logging.info(f'开始读取{temp}文件夹中的文件')
        if os.path.exists(temp):
            files = os.listdir(temp)
            for file in files:
                if file.endswith('.xlsx'):
                    # 读取文件
                    new_data = Excel.read_xls_to_dict(
                        os.path.join(temp, file))
                    data.extend(new_data)
            mounts = len(data)
            logging.info(f'已读取{temp}文件夹中【{mounts}】条数据')
        else:
            logging.info(f'{temp}文件夹不存在')
        return data

    # 保存文件
    def save(folder=r'data', items=[], random=True):
        path = os.path.join(config.folder, folder)
        logging.info(f'保存文件到目录：{path}')
        if not os.path.exists(path):
            logging.info(f'创建目录：{path}')
            os.mkdir(path)
        # 如果items是dataframe类型，则直接保存
        if isinstance(items, pd.DataFrame):
            df = items
        else:
            # 将字典列表直接转换为DataFrame
            df = pd.DataFrame.from_records(items)
        # 将nan替换为空字符串，不区分大小写
        df = df.replace(re.compile('nan', re.I), '')
        try:
            # 去除空行
            df = df.dropna(how='any', subset=['url', 'imgurl', 'title'])
        except Exception as e:
            logging.exception(f'Failed to drop empty rows: {e}')
        # 去重
        df = df.drop_duplicates(subset=['url'])

        if random:
            excel_path = os.path.join(
                path, f'items_{Excel.timestamp}.xlsx')
        else:
            excel_path = os.path.join(
                path, f'items.xlsx')
        logging.info(f"正在保存文件: {excel_path}")
        try:
            df.to_excel(excel_path, index=False)
            return excel_path
        except:
            logging.exception("Failed to save Excel file")

    # 删除temp文件夹
    def remove_temp(folder='temp'):
        temp = os.path.join(config.folder, folder)
        if os.path.exists(temp):
            logging.info(f'删除{temp}文件夹')
            shutil.rmtree(temp)
        else:
            logging.info(f'{temp}文件夹不存在')

    # 对items2的数据，根据'url'字段唯一性合并到items1中，返回合并后的数组
    def merge(items1, items2):
        if not len(items1):
            items = items2
        else:
            items = items1
            # 获取items1中pubtime最近的时间戳
            max_timestamp = max([i['pubtime'] for i in items])
            # 获取items1中的所有url
            urls = [i['url'] for i in items]
            for item in items2:
                if item['url'] in urls:
                    logging.info(f'已存在新闻：{item["title"]}')
                    continue
                # 如果item的时间戳小于items1中的最大时间戳，则跳过
                if item['pubtime'] <= max_timestamp:
                    logging.info(f'已检测新闻：{item["title"]}')
                    continue
                items.append(item)
        for item in items:
            # 检查数据完整性
            if not Excel.is_complete(item):
                # items中删除item
                logging.info(f'数据不完整：{item["title"]}')
                items.remove(item)
        logging.info(f'合并后的数据量：{len(items)}')
        return items

    # 判断item的'url'、'imgurl'、'title'、'intro'字段是否完整
    def is_complete(item):
        # 判断item中是否存在nan字段
        # for key, value in item.items():
        # if re.search('nan', str(value), re.I):
        #     logging.warning(f'存在nan字段：{item}')
        # if re.search('null', str(value), re.I):
        #     logging.warning(f'存在null字段：{item}')
        # if re.search('none', str(value), re.I):
        #     logging.warning(f'存在null字段：{item}')
        if item['url'] and item['imgurl'] and item['title'] and item['intro'] and len(item['intro']) > 80:
            # item是否存在pubtime或published_at字段，且不为0
            if 'pubtime' in item.keys() and item['pubtime']:
                return True
            if 'published_at' in item.keys() and item['published_at']:
                return True
        return False

    # 计算时间差
    def time_gap(timestamp):
        # 将时间戳转换为 datetime 对象
        dt = datetime.fromtimestamp(timestamp)
        # 计算与当前时间的差
        delta = datetime.now() - dt
        return delta.days

    # 转换时间格式
    def convert_time(timestamp):
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    # 提取评分结果中的指标数据
    def extract(text):
        result = {}
        # # 提取关键词、是否热搜、理由
        # pattern = r"关键词(?P<keywords>.*?)\n.*?热搜.*?(?P<hot_related>是|否).*?理由(?P<reason>[\s\S]*)"
        # match = re.search(pattern, text, re.DOTALL)
        # result = match.groupdict() if match else {}
        # # 后处理关键词
        # if result and result['keywords']:
        #     result['keywords'] = re.sub(r'[,，、]', ' ', result['keywords'])
        #     result['keywords'] = re.sub(
        #         r'[^\w\s]', '', result['keywords']).strip()
        # logging.debug(f"关键词：{result['keywords']}")
        # # 后处理理由
        # if result and result['reason']:
        #     # 替换冒号
        #     result['reason'] = re.sub('[：:]', '', result['reason']).strip()
        # logging.debug(f"理由：{result['reason']}")
        # 提取指标数据
        values = {k: v for v, k in enumerate(Excel.columns)}
        patterns = [
            r"时效性.*?(?P<timing>\d)分", r"新闻性.*?(?P<nvalue>\d)分", r"实用性.*?(?P<practical>\d)分", r"客观性.*?(?P<objective>\d)分", r"地域性.*?(?P<local>\d)分", r'商业性.*?(?P<business>\d)分', r"娱乐性.*?(?P<joy>\d)分", r'话题度.*?(?P<topic>\d)分'
            # ,r'总分.*?(?P<mark>\d+)分'
        ]
        for item, value in values.items():
            match = re.search(patterns[value], text)
            result[item] = int(match.group(item)) if match else 0
        # 计算总分
        result['mark'] = result['timing'] + result['nvalue'] + result['practical'] + \
            result['objective'] + result['joy'] + result['topic'] - \
            result['local'] - result['business']
        logging.info(f"计算总分为: {result['mark']}分\n")
        return result


if __name__ == "__main__":
    text = '''
        关键词: OPPO    Find X6 全球首发。
        热搜关联性: 否。

        时效性: 4分。新品发布是一个高时效性的事件，而且该新品还未发布，预热期间也受到了关注。
        新闻性: 3分。介绍了一个新品的基本信息，但并没有详细介绍其特点和功能，新闻价值略低。
        实用性: 2分。介绍了一个新品的发布时间，对读者的实际应用价值不高。
        客观性: 5分。该新闻以事实为基础，没有使用主观或情绪化的语言。
        地域性: 2分。该新闻只涉及一个品牌和一个产品系列，对不同受众的吸引力不高。
        商业性: 1分。该新闻仅介绍了单一产品，没有公益性的视角。
        娱乐性: 2分。该新闻仅介绍了单一产品，没有娱乐性。
        话题度: 2分。该新闻未出现在今日热搜，话题度不高。
        总分: 19分。

        评分理由: 该新闻在时效性方面得分较高，但在新闻性、实用性、地域性和公益性方面得分较低。虽然客观性方面得分较高，但是该新闻仅仅介绍了单一产品，完全没有公益性的视角，是一篇软性广告。话题度方面得分也不高。综上所述，该新闻总分较低。
    '''
    Excel.extract(text)
