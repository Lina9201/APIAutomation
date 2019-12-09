# -*- coding: utf-8 -*-
# @Time    : 2019/10/8 14:49
# @Author  : zhuxuefei

import pytest
import requests
import json
import allure
import os
from config import Conf
from common.get_excel_data import OperationExcleData
from utils.AssertUtil import AssertUtil

# 创建数据中心请求url
createDataCenter_url = "/admin/v1/regions"

# 获取创建数据中心请求参数数据
testdata_path = Conf.get_testdata_path()
excelFile = testdata_path + os.sep + "物理资源.xlsx"
sheetName = "添加数据中心"
datacenter_data = OperationExcleData(excelFile, sheetName).getCaseList()

@pytest.mark.run(order=1)
@pytest.mark.parametrize("datacenter_data", datacenter_data)
def test_create_datacenter(uri, headers, datacenter_data):
    """
    创建数据中心接口
    :param ip:
    :param port:
    :param headers:
    :param datacenter_data:测试用例
    :return:
    """
    createDataCenter_response = requests.post(url=uri + createDataCenter_url,
                                         data=json.dumps(datacenter_data),
                                         headers=headers)
    code = createDataCenter_response.status_code
    AssertUtil().assert_code(code, 200)
    allure.dynamic.feature(excelFile)
    allure.dynamic.story(sheetName)


def get_datacenterid(uri, headers, datacentername):
    """
    根据创建数据中心名称获取所属ID
    :param ip:
    :param port:
    :param headers:
    :return:
    """
    getDataCenterId_response = requests.get(url=uri + createDataCenter_url,
                                   headers=headers).json()
    for dc in getDataCenterId_response["data"]:
        if dc["name"] == datacentername:
            return dc["id"]


def get_datacenter(uri, headers):
    getDataCenter_response = requests.get(url=uri + createDataCenter_url,
                                            headers=headers).json()
    return getDataCenter_response["data"]


if __name__ == '__main__':
    report_raw_path = "../../report/allure_raw"
    testdata_path = Conf.get_testdata_path()
    excelFile = testdata_path + "物理资源.xlsx"
    print(excelFile)



