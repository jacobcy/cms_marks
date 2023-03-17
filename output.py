# -*- coding: utf-8 -*-

import pandas as pd
from setting import config
import re
import time
timestamp = int(time.time())


def toJson(excel_path):

    # 读取 Excel 文件
    df = pd.read_excel(excel_path)

    # 删除不需要的列
    df = df.drop(columns=['imgurl', 'pubtime', 'intro', 'url'])

    # 重新生成指标数据
    try:
        df = df.drop(columns=['keywords', 'hot_related', 'reason', 'mark'])
        df = df.drop(columns=['timeliness', 'news_value', 'practicality', 'objectivity',
                     'wideness', 'diversity', 'public', 'entertainment', 'popularity'])
    except:
        pass

    # 转换为 JSON 格式
    items = df.to_dict('records')

    for item in items:
        evaluate = item['evaluate']
        # print(target)
        res = extract(evaluate)
        if res:
            for label, value in res.items():
                item[label] = value
                # print(label, value)

    # 将json数据展平
    df = pd.json_normalize(items)

    # 表头重命名为中文
    df1 = df.drop(columns=['evaluate'])
    try:
        df1 = df1.rename(columns={
            'timeliness': '时效',
            'news_value': '新闻',
            'practicality': '实用',
            'objectivity': '客观',
            'wideness': '广泛',
            'diversity': '多元',
            'public': '公益',
            'entertainment': '娱乐',
            'popularity': '流行'
        })
    except:
        pass

    # 保存json格式的csv文件，便于查看评分
    json_path = config.path + f'output_{timestamp}.csv'
    df1.to_csv(json_path, index=False, encoding='utf-8-sig')

    # 删除多余的列
    try:
        df = df.drop(columns=['source_from', 'published_at'])
        df = df.drop(columns=['keywords', 'hot_related', 'reason', 'mark'])
        df = df.drop(columns=['timeliness', 'news_value', 'practicality', 'objectivity',
                     'wideness', 'diversity', 'public', 'entertainment', 'popularity'])
    except:
        pass
    df = df.rename(columns={'title': 'prompt', 'evaluate': 'completion'})

    # 保存为jsonL格式的csv文件，用于上传训练
    jsonL_path = config.path + f'training_data_{timestamp}.csv'
    with open(jsonL_path, 'w', encoding='utf-8') as f:
        for index, row in df.iterrows():
            # 将每行数据转换为json格式的字符串
            json_str = row.to_json(force_ascii=False)
            # 写入文件，并添加换行符
            f.write(json_str)
            f.write('\n')


def toExcel(sorted_results):

    # 将DataFrame存入Excel文件中
    df = pd.DataFrame(sorted_results)
    excel_path = config.path + f'items_{timestamp}.xlsx'
    try:
        df.to_excel(excel_path, index=False)
        return excel_path

    except Exception as e:
        print(e)


def extract(text):

    # 预处理输入内容，去除标点符号
    # text = re.sub(r'[^\w\s]', '', text)

    pattern = r"关键词(?P<keywords>.*?)\n.*?热搜.*?(?P<hot_related>是|否).*?理由(?P<reason>[\s\S]*)"
    match = re.search(pattern, text, re.DOTALL)
    result = match.groupdict() if match else {}

    if result['keywords']:
        result['keywords'] = re.sub(r'[,，、]', ' ', result['keywords'])
        result['keywords'] = re.sub(r'[^\w\s]', '', result['keywords']).strip()

    if result['reason']:
        # 替换冒号
        result['reason'] = re.sub('[：:]', '', result['reason']).strip()

    values = {'timeliness': 0, 'news_value': 1, 'practicality': 2,
              'objectivity': 3, 'wideness': 4, 'diversity': 5, 'public': 6, 'entertainment': 7, 'popularity': 8, 'mark': 9}

    patterns = [r"时效性.*?(?P<timeliness>\d)分", r"新闻性.*?(?P<news_value>\d)分", r"实用性.*?(?P<practicality>\d)分", r"客观性.*?(?P<objectivity>\d)分",
                r"广泛性.*?(?P<wideness>\d)分", r'多元化.*?(?P<diversity>\d)分', r"公益性.*?(?P<public>\d)分", r"娱乐性.*?(?P<entertainment>\d)分", r'流行度.*?(?P<popularity>\d)分', r'总分.*?(?P<mark>\d+)分']

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

        公益性: 1分。该新闻仅介绍了单一产品，没有公益性的视角。

        流行度: 2分。该新闻未出现在今日热搜，流行度不高。

        总分: 19分。

        简述评分原因: 该新闻在时效性方面得分较高，但在新闻性、实用性、广泛性和公益性方面得分较低。虽然客观性方面得分较高，但是该新闻仅仅介绍了单一产品，完全没有公益性的视角，是一篇软性广告。流行度方面得分也不高。综上所述，该新闻总分较低。
    '''
    toJson(config.path + 'items.xlsx')
