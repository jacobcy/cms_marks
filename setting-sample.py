# -*- coding: utf-8 -*-
import os


class config:

    # 获取脚本的本地路径
    folder = os.path.dirname(os.path.abspath(__file__))

    # cms参数
    url = ""
    email = ""
    password = ""
    execute_url = ''
    total_node_num = 60

    apis = []
    api_content_number = 32

    # chatgpt部分
    keys = []
    waiting_time = 5
