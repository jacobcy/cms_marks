from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# 创建一个 FirefoxOptions 实例
options = Options()

# 设置 Firefox 二进制文件路径
options.binary_location = 'C:\Windows\System32\firefox.exe'

# 创建一个 FirefoxProfile 实例
profile = FirefoxProfile()

# 创建一个 Firefox 浏览器实例
browser = webdriver.Firefox(options=options)

# 打开一个网址
url = "https://cms2.firefoxchina.cn"
browser.get(url)

# 关闭浏览器
# browser.quit()
