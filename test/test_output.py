# 对../outopu.py的测试
import os
import unittest
from output import Excel
import pandas as pd


class TestExtract(unittest.TestCase):

    def setUp(self):
        self.excel = Excel()
        self.text = '''
        关键词: OPPO,Find、X6，全球首发。
        热搜关联性: 否。

        时效性: 4分。新品发布是一个高时效性的事件，而且该新品还未发布，预热期间也受到了关注。
        新闻性: 3分。介绍了一个新品的基本信息，但并没有详细介绍其特点和功能，新闻价值略低。
        实用性: 2分。介绍了一个新品的发布时间，对读者的实际应用价值不高。
        客观性: 5分。该新闻以事实为基础，没有使用主观或情绪化的语言。
        地域性: 2分。该新闻只涉及一个品牌和一个产品系列，对不同受众的吸引力不高。
        商业性: 1分。该新闻仅介绍了单一产品，没有公益性的视角。
        娱乐性: 2分。该新闻仅介绍了单一产品，没有娱乐性。
        话题度: 2分。该新闻未出现在今日热搜，话题度不高。

        评分理由: 该新闻在时效性方面得分较高，但在新闻性、实用性、广泛性和公益性方面得分较低。虽然客观性方面得分较高，但是该新闻仅仅介绍了单一产品，完全没有公益性的视角，是一篇软性广告。话题度方面得分也不高。综上所述，该新闻总分较低。
    '''
        self.data = self.excel.extract(self.text)

    def test_extract_keywords(self):
        self.assertEqual(self.data['keywords'], 'OPPO Find X6 全球首发')

    def test_extract_reason(self):
        self.assertEqual(
            self.data['reason'], '该新闻在时效性方面得分较高，但在新闻性、实用性、广泛性和公益性方面得分较低。虽然客观性方面得分较高，但是该新闻仅仅介绍了单一产品，完全没有公益性的视角，是一篇软性广告。话题度方面得分也不高。综上所述，该新闻总分较低。')

    def test_extract_timing(self):
        self.assertEqual(self.data['timing'], 4)

    def test_extract_nvalue(self):
        self.assertEqual(self.data['nvalue'], 3)

    def test_extract_practical(self):
        self.assertEqual(self.data['practical'], 2)

    def test_extract_objective(self):
        self.assertEqual(self.data['objective'], 5)

    def test_extract_local(self):
        self.assertEqual(self.data['local'], 2)

    def test_extract_business(self):
        self.assertEqual(self.data['business'], 1)

    def test_extract_joy(self):
        self.assertEqual(self.data['joy'], 2)

    def test_extract_topic(self):
        self.assertEqual(self.data['topic'], 2)

    def test_save(self):
        data = [self.data]

        # 测试保存数据到Excel文件
        excel_path = self.excel.save('test', data)

        # 测试文件是否存在
        self.assertTrue(os.path.isfile(excel_path))

        # 测试文件是否能够正常打开和读取
        df = pd.read_excel(excel_path)
        self.assertEqual(list(df.columns), list(self.data.keys()))


if __name__ == 'main':
    unittest.main()
    # 字符串转为json
    # json.dumps(data, ensure_ascii=False)