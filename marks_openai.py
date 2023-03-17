#!python

from chrome import cms_update
from setting import config
from output import toExcel, extract

import requests
import time
from datetime import datetime
import openai

# 使用 API 密钥进行身份验证
openai.api_key = config.key


def time_gap(timestamp):
    # 将时间戳转换为 datetime 对象
    dt = datetime.fromtimestamp(timestamp)

    # 计算与当前时间的差
    delta = datetime.now() - dt

    # 计算差值的小时数
    hours_diff = delta.seconds // 3600
    return hours_diff


def getRate(items):
    results = []
    conversation = config.conversation
    # 循环遍历标题数组
    for item in items:
        if item['url'] and item['imgurl'] and item['title'] and item['intro'] and len(item['intro']) > 100:
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
            completion = getResult(conversation)
            if not completion:
                continue

            item['evaluate'] = completion

            # 转换时间格式
            ptm = item['pubtime']
            dt = datetime.fromtimestamp(ptm)
            item["published_at"] = dt.strftime("%Y-%m-%d %H:%M:%S")

            # 总分默认为10分
            mark = 18

            # 抽取completion信息
            res = extract(completion)
            if res:
                for label, value in res.items():
                    item[label] = value

            # 根据时间差调整分数
            mark = item['mark']
            if time_gap(ptm) > 48:
                mark = mark - 2
            elif time_gap(ptm) > 24:
                mark = mark - 1
            elif time_gap(ptm) > 12:
                mark = mark
            else:
                mark = mark + 1
            item['mark'] = mark

            print(title, '\n', completion)
            results.append(item)
            time.sleep(3)

    # 返回打分结果
    return results


# 根据内容获取评分结果


def getResult(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=prompt,  temperature=0.1)
        # 获取结果字符串
        text = completion.choices[0].message.content.strip()

        # 返回评分结果
        return text

    except Exception as e:
        print(e)


def main():

    apis = config.apis

    results = []

    for api in apis:
        try:
            # 发送 API 请求并获取 JSON 响应
            response = requests.get(api)
            if response:
                # 将响应解析为JSON格式，并取出items中的前xx个元素
                items = response.json()['items'][:32]

                # 获取评分结果
                result = getRate(items)

                if result:
                    results.extend(result)

        except Exception as e:
            print(e)

    if results and len(results) >= 4:

        # 汇总后对总分进行排序
        sorted_results = sorted(
            results, key=lambda x: x['mark'], reverse=True)

        # 备份获取的数据
        toExcel(sorted_results)

        cms = cms_update(sorted_results)
        cms.update()

    else:
        print('There are no sufficient news to update!')


if __name__ == "__main__":

    main()
