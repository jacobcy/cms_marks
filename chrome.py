#!python

import re
import json
import time
import logging

# 导入selenium模块
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException

from setting import config
from output import Excel


class CMS:
    def __init__(self, data=[]):
        # 先读取temp中的excel数据
        if not data:
            data = Excel.read_data(r'data')
        # 如果没有数据,则退出
        if not data:
            logging.info('No data available!')
            exit(0)
        # 判断data中的数据是否完整
        for item in data:
            if not Excel.is_complete(item):
                data.pop(item)

        # 按照总分进行排序
        # data = sorted(data, key=lambda x: x['mark'], reverse=True)
        self.data = data
        self.num = 0
        # 打印数据
        logging.info(json.dumps(self.data[:1], indent=4, ensure_ascii=False))

        logging.info('正在打开浏览器...\n')
        # 创建一个Options对象，并添加detach选项
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        # 添加参数"–ignore-certificate-errors"
        chrome_options.add_argument("--ignore-certificate-errors")
        # 创建一个WebDriver对象，并传入Options对象
        self.driver = webdriver.Chrome(options=chrome_options)
        # 等待页面加载
        self.driver.implicitly_wait(5)
        self.wait = WebDriverWait(self.driver, 5)

    # 点击第一个链接，等待第二个链接出现
    def click_and_wait(self, css_selector1, css_selector2):
        for i in range(2):
            time.sleep(2)
            # 点击指定的链接
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, css_selector1).click()
            except Exception as e:
                logging.exception(f"无法点击链接 {css_selector1}: {e}")
            try:
                self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, css_selector2)))
                return
            except Exception as e:
                logging.exception(f"无法找到下一个链接 {css_selector2}: {e}")
        # 如果超过最大重试次数仍然无法进入下一步，则抛出异常
        raise Exception("无法进入下一步")

    def click_and_wait_sequence(self, clicks):
        for i in range(len(clicks)-1):
            self.click_and_wait(clicks[i], clicks[i+1])

    def login(self):
        # 打开网站并输入用户名和密码
        self.driver.get(config.url)
        time.sleep(2)
        # 输入用户名和密码
        username = self.driver.find_element(By.ID, "email")
        username.send_keys(config.email)
        password = self.driver.find_element(By.ID, "password")
        password.send_keys(config.password)
        time.sleep(2)
        submit_button = self.driver.find_element(By.ID, "login-submit")
        submit_button.click()

    # 输入数据
    def input_data(self):
        inputs = ['title', 'url', 'imgurl',
                  'intro', 'published_at', 'source_from']
        item = self.data[self.num-1]
        if not Excel.is_complete(item):
            logging.error(f"数据不完整: {item}")
            return False
        logging.info(f"正在输入数据: {item['title']}")
        for j in range(len(inputs)):
            if inputs[j] not in item or re.search('nan', str(inputs[j]), re.I):
                logging.error(f"数据缺失: {inputs[j]}")
                return False
            t = item[inputs[j]]
            time.sleep(1)
            # 在输入框中输入文本
            input_box = self.driver.find_element(
                By.ID, inputs[j])
            input_box.clear()
            try:
                input_box.send_keys(t)
            except:
                logging.exception(f"无法输入数据: {t}")
        # 点击提交按钮
        time.sleep(1)
        submit_button = self.driver.find_element(By.CSS_SELECTOR,
                                                 "li.space:nth-child(24) > input[type='submit']")
        submit_button.click()
        try:
            # 等待弹窗出现并点击确定按钮
            self.wait.until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            logging.debug('点击确定按钮')
            alert.accept()
            time.sleep(1)
            return True
        except Exception as e:
            logging.warning(f"无法提交，可能数据重复")
            return False

    # 备份执行数据
    def backup(self):
        # 备份数据
        path = Excel.save('data', self.data, False)
        Excel.toJson(path)
        # 清空temp文件夹
        # Excel.remove_temp()
        # Excel.remove_temp('temp_api')
        time.sleep(config.waiting_time)
        # 关闭浏览器
        self.driver.quit()

    # 利用selenium更新cms中的数据
    def update(self):
        # 如果没有数据需要更新，则退出
        if not self.data:
            logging.info('没有数据需要更新')
            return
        # 登录
        self.login()
        # 点击链接并等待页面加载
        clicks = [
            '.nav > li:nth-child(2) > a:nth-child(1)',
            'li.flex-between:nth-child(4) > a:nth-child(2)',
            '.tree > li:nth-child(2) > div:nth-child(1) > span:nth-child(1) > a:nth-child(3)',
            'ul.tree:nth-child(2) > li:nth-child(1) > div:nth-child(1) > span:nth-child(1) > a:nth-child(2)'
        ]
        self.click_and_wait_sequence(clicks)
        # 遍历子节点，填入更新数据
        for i in range(config.total_node_num):

            # 检查是否有足够的数据
            self.num += 1
            if self.num > len(self.data):
                logging.error('没有足够的数据继续更新')
                break
            # 点击子节点
            item = self.driver.find_element(
                By.CSS_SELECTOR, f"ul.tree:nth-child(2) > li:nth-child({i+1}) > div:nth-child(1) > span:nth-child(1) > a:nth-child(2)")
            if not item:
                break
            # 切换到新页面
            handles = self.driver.window_handles
            while len(handles) < 2:
                item.click()
                time.sleep(2)
                handles = self.driver.window_handles
            try:
                self.driver.switch_to.window(handles[-1])
            except NoSuchWindowException:
                continue
            # 输入数据
            logging.info(f"正在更新第 {self.num} 条数据")
            summit = self.input_data()
            if not summit:
                while True:
                    self.num += 1
                    logging.warning(f"提交失败，尝试第 {self.num} 条数据")
                    summit = self.input_data()
                    if summit:
                        break
            logging.info("数据更新成功,确定后返回原页面")
            # 检查弹窗页面是否关闭，等待5s
            handles = self.driver.window_handles
            for k in range(5):
                if len(handles) > 1:
                    logging.warning(f"弹窗未关闭，等待 {5-k} 秒")
                    time.sleep(1)
                    handles = self.driver.window_handles
            # 强制返回原页面
            if len(handles) > 1:
                logging.warning(f"手动关闭弹窗页面，返回原页面")
                self.driver.close()
            try:
                self.driver.switch_to.window(handles[0])
            except NoSuchWindowException:
                logging.error(f"无法切换到原页面,强制切换")
                self.driver.switch_to.default_content()
        # 执行更新
        self.driver.get(config.execute_url)
        # 保存数据并关闭浏览器
        self.backup()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        encoding='utf-8')
    cms = CMS()
    cms.update()
