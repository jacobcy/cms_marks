#!python
import os
import time

import logging

from setting import config
from output import Excel
from apis import API
from chrome import CMS


class Marks:
    def __init__(self, items=[]):
        logging.info(f'Start running...\n')
        # 如果没有传入items
        if not items:
            # 从excel中获取数据
            old_items = Excel.read_temp('temp_api')
            # 从api中获取数据最新数据
            new_items = API.get_news(config.api_content_number)
            # 合并数据
            raw_items = Excel.merge(old_items, new_items)
            # 筛选出24小时内的数据
            for item in raw_items:
                ptm = Excel.time_gap(item['pubtime'])
                if ptm <= 24:
                    items.append(item)
        # 选取最多200条数据
        self.items = items[:200]

    @staticmethod
    def get_conversation():
        cs = [{
            'role': 'system', 'content': f'''
        请扮演一名网站编辑，评估新闻质量：
        1、提炼新闻关键词。
        2、判断新闻主题是否与“今日热搜”相关。
        3、使用以下指标对新闻进行评分(分值范围1-9分):
            a. 时效性：衡量新闻事件是否紧迫及时。
            b. 新闻性：评估新闻标题是否引人瞩目、吸引眼球。
            c. 实用性：考虑内容对读者的实际价值，如提供有益的见解或解决方案。
            d. 客观性：根据新闻来源，判断内容在陈述事实和观点时是否公正和中立。
            e. 地域性：评估新闻事件的地域影响范围，地域范围越小，该项分值越高。
            f. 商业性：考虑报道内容是否对某类产品或品牌进行广告宣传，根据广告效果打分。
            g. 娱乐性：考虑内容在吸引读者兴趣、引发情感反应方面的表现。
            h. 话题度：衡量内容与“今日热搜”的相关性，如果不相关八卦内容更具有话题度。

        今日热搜:{API.aggre()}

        按照以下格式回复:
        关键词: aaa\tbbb\tccc
        热搜: 是|否
        时效性: x分\t新闻性: x分\t实用性: x分\t客观性: x分\t地域性: x分\t商业性: x分\t娱乐性: x分\t话题度: x分
        评价理由: zzzzzzz
        '''}]
        logging.info(cs[0]['content'])
        return cs

    # 给新闻打分
    def getRate(self, items):
        error = 0
        result = []
        # 获取对话内容
        cs = Marks.get_conversation()
        # 循环遍历标题数组
        for item in items:
            # 如果字段不完整则跳过
            if not Excel.is_complete(item):
                continue
            # 计算剩余的新闻数量，并打印日志
            num = items.index(item)
            num_remain = len(items) - num
            logging.info(f'正在处理第{num}条，剩余数量:{num_remain}')

            # 获取新闻标题和简介
            title = item['title']
            intro = item['intro']
            # 重命from名字段后保存
            source_from = item.pop('from')
            item["source_from"] = source_from
            cs = cs[:1]
            cs.append({
                'role': 'user',
                'content': f'新闻标题:{title}\n新闻介绍:{intro}\n新闻来源:{source_from}'
            })
            # 调用 getResult() 方法获取 ChatGPT 返回的结果，等待其返回
            completion = API.get_result(cs)
            if not completion:
                logging.info('无法获取反馈结果!\n')
                error += 1
                if error > 3:
                    logging.exception('连续3次获取排序结果失败!\n')
                    return result
                else:
                    continue
            # 保存打分结果
            item['evaluate'] = completion
            logging.info(f"{title}\n{completion}")
            print(f"{title}\n{completion}")
            # 转换时间格式
            item["published_at"] = Excel.convert_time(item.pop('pubtime'))
            # 抽取completion信息
            res = Excel.extract(completion)
            if res:
                for label, value in res.items():
                    item[label] = value
            print(f'总分：{item["mark"]}\n')
            result.append(item)
            time.sleep(config.waiting_time)
        # 返回打分结果
        return result

    # 主函数
    def main(self):
        data = []
        # 获取评分结果
        result = self.getRate(self.items)
        data.extend(result)
        # 备份临时数据
        Excel.save('temp', data)
        if data and len(data) >= 12:
            # 更新CMS
            CMS(data).update()
        else:
            logging.exception('There are no sufficient news to update!')


if __name__ == "__main__":
    # 日志配置
    times = int(time.time())
    log_path = os.path.join(config.folder, 'log', f'myapp_{times}.log')
    print(log_path)

    logging.basicConfig(
        level=logging.INFO,
        filename=log_path,
        filemode='w',
        format='%(asctime)s - %(levelname)s: %(message)s',
        encoding='utf-8')

    Marks().main()
