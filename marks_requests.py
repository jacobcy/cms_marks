import time
import requests
import json
import re
import pandas as pd
from setting import Excel

accessToken = Excel.key


def getRate(values):
    try:
        # 循环遍历标题数组
        for value in values:
            prompt = [
                {'role': 'system', 'content': "我希望你扮演网站编辑,根据文章内容的吸引力和流行趋势评分,范围为1到100,不要解释。"}]
            question = value['intro']
            print(question)

            prompt.append({'role': 'user', 'content': question})
            # 调用 getResult() 方法获取 ChatGPT 返回的结果，等待其返回
            answer = getResult(prompt)
            print(answer)

            value['mark'] = answer
            time.sleep(3)
        values = sorted(
            values, key=lambda x: x['value'], reverse=True)
        top_10_items = values[:3]
        print(top_10_items)
        return values
    except Exception as e:
        print(e)


# 根据对话ID和标题获取评分结果


def getResult(prompt):
    try:
        # 发送 POST 请求
        response = requests.post('https://api.openai.com/v1/chat/completions', headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {accessToken}"
        }, data=json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": prompt,
            "max_tokens": 100,
            "temperature": 0.3,
            "top_p": 1,
            "n": 1
        }))

        response_json = json.loads(response.text)
        if "choices" in response_json and len(response_json["choices"]) > 0:
            completion = response_json["choices"][0]
            result = completion["message"]["content"]

            # 定义一个正则表达式，用于匹配两位数字
            pattern = re.compile(r'\b\d{2}\b')

            # 使用正则表达式搜索变量中是否包含两位数字
            match = pattern.search(result)

            if match:
                # 如果匹配到了两位数字，则取出第一个匹配结果
                score = match.group(0)
                return score
        else:
            print(response_json["error"]["message"])
        # 如果没有匹配到两位数字，则将结果设置为0
        score = 0
        # 返回评分结果
        return score
    except Exception as e:
        print(e)


# 发送 API 请求并获取 JSON 响应
response = requests.get('https://mini.eastday.com/qid02157/keji-firefox.js')

# 将响应解析为JSON格式，并取出items中的前10个元素
items = response.json(encoding='utf-8')['items'][:10]

# 获取评分结果
items = getRate(items)

# 将items存入DataFrame中
df = pd.DataFrame(items)

# 将DataFrame存入Excel文件中
df.to_excel('items.xlsx', index=False)
