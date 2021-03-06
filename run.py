# -*- coding: utf-8 -*-
# @Time    : 2019/10/14 13:38
# @Author  : zhuxuefei

import os
import pytest
from config import Conf
from common.get_report import allure_report

if __name__=='__main__':
    report_path = Conf.get_report_path()+os.sep+"result"
    report_html = Conf.get_report_path()+os.sep+"html"
    pytest.main(["-m cmdb","--alluredir", report_path])
    allure_report(report_path, report_html)

