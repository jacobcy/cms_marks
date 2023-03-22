# 对../outopu.py的测试

import unittest
from output import Excel


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
        广泛性: 2分。该新闻只涉及一个品牌和一个产品系列，对不同受众的吸引力不高。
        多元化: 1分。该新闻仅介绍了单一产品，没有公益性的视角。
        娱乐性: 2分。该新闻仅介绍了单一产品，没有娱乐性。
        流行度: 2分。该新闻未出现在今日热搜，流行度不高。
        总分: 19分。

        评分理由: 该新闻在时效性方面得分较高，但在新闻性、实用性、广泛性和公益性方面得分较低。虽然客观性方面得分较高，但是该新闻仅仅介绍了单一产品，完全没有公益性的视角，是一篇软性广告。流行度方面得分也不高。综上所述，该新闻总分较低。
    '''

    def test_extract_keywords(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['keywords'], 'OPPO Find X6 全球首发')

    def test_extract_reason(self):
        result = self.excel.extract(self.text)
        self.assertEqual(
            result['reason'], '该新闻在时效性方面得分较高，但在新闻性、实用性、广泛性和公益性方面得分较低。虽然客观性方面得分较高，但是该新闻仅仅介绍了单一产品，完全没有公益性的视角，是一篇软性广告。流行度方面得分也不高。综上所述，该新闻总分较低。')

    def test_extract_timeliness(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['timeliness'], 4)

    def test_extract_news_value(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['news_value'], 3)

    def test_extract_practicality(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['practicality'], 2)

    def test_extract_objectivity(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['objectivity'], 5)

    def test_extract_wideness(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['wideness'], 2)

    def test_extract_diversity(self):

        result = self.excel.extract(self.text)
        self.assertEqual(result['diversity'], 1)

    def test_extract_entertainment(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['entertainment'], 2)

    def test_extract_popularity(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['popularity'], 2)

    def test_extract_total_mark(self):
        result = self.excel.extract(self.text)
        self.assertEqual(result['mark'], 19)


if __name__ == 'main':
    unittest.main()
