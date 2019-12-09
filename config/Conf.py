# -*- coding: utf-8 -*-
# @Time    : 2019/10/26 20:54
# @Author  : zhuxuefei

import os
from utils.YamlUtil import YamlReader

# 获取当前项目的绝对路径
current = os.path.abspath(__file__)
print(current)
BASE_DIR = os.path.dirname(os.path.dirname(current))
print(BASE_DIR)

# 定义config目录的路径
_config_path = BASE_DIR + os.sep + "config"

# 定义report目录的路径
_report_path = BASE_DIR + os.sep + "report"

# 定义test_data目录的路径
_testdata_path = BASE_DIR + os.sep + "test_data"

# 定义config.yml文件的路径
_config_file = _config_path + os.sep + "conf.yml"


def get_config_path():
    return _config_path


def get_config_file():
    return _config_file


def get_report_path():
    return _report_path


def get_testdata_path():
    return _testdata_path

# 读取配置文件
class ConfigYaml:
    def __init__(self):
        self.config = YamlReader((get_config_file())).yamldata()


    def get_db_config(self, db_alias):
        return self.config[db_alias]


