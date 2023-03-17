#!python

# 导入selenium模块
import time
import pandas as pd
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException
from setting import config


class cms_update():
    def __init__(self, data=[]):

        if not data:
            # 读取 Excel 文件
            df = pd.read_excel(config.path + r"items.xlsx")
            # 转换为 JSON 格式
            data = df.to_dict('records')

        print(json.dumps(data[:1], indent=4, ensure_ascii=False))
        # 最多36个节点
        self.data = data[:36]

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
                print(f"无法点击链接 {css_selector1}: {e}")

            try:
                self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, css_selector2)))
                return
            except Exception as e:
                print(f"无法找到下一个链接 {css_selector2}: {e}")

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

    # 利用selenium更新cms中的数据

    def update(self):

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
        for i in range(len(self.data)):
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

            inputs = ['title', 'url', 'imgurl',
                      'intro', 'published_at', 'source_from']

            for j in range(len(inputs)):
                if self.data[i][inputs[j]]:
                    time.sleep(1)
                    # 在输入框中输入文本
                    input_box = self.driver.find_element(
                        By.ID, inputs[j])
                    input_box.clear()
                    input_box.send_keys(self.data[i][inputs[j]])

            # 点击提交按钮
            time.sleep(1)
            submit_button = self.driver.find_element(By.CSS_SELECTOR,
                                                     "li.space:nth-child(24) > input[type='submit']")
            submit_button.click()

            try:
                # 等待弹窗出现并点击确定按钮
                self.wait.until(EC.alert_is_present())
                time.sleep(1)
                alert = self.driver.switch_to.alert
                alert.accept()

                # 关闭新页面并切换回原来的页面
                handles = self.driver.window_handles
                while len(handles) > 1:
                    time.sleep(1)
                    handles = self.driver.window_handles
            except:
                self.driver.close()
                time.sleep(2)
                handles = self.driver.window_handles

            try:
                self.driver.switch_to.window(handles[0])
            except NoSuchWindowException:
                self.driver.switch_to.default_content()

        time.sleep(5)
        self.driver.get(config.execute_url)

        # 关闭浏览器
        self.driver.quit()


if __name__ == "__main__":
    cms = cms_update()
    cms.update()
