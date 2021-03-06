# -*- coding: utf-8 -*-
# @Time    : 2020/1/6 9:50
# @Author  : zhuxuefei
import os
from config import Conf
import pytest
from common.get_excel_data import OperationExcleData
import requests
from common.get_db_data import init_arangodb
from utils.LogUtil import my_log
from utils.AssertUtil import AssertUtil
import allure

# 配置项类型url
base_category_url = "/admin/v1/categories"
categorys_tree_url = "/admin/v1/categories/tree/?sortField=createTime&sortOrder=desc"
testdata_path = Conf.get_testdata_path()
excelFile = testdata_path + os.sep + "配置管理.xlsx"
category_data = OperationExcleData(excelFile, "创建配置项类型").getcase_tuple()
update_category_data = OperationExcleData(excelFile, "编辑配置项类型").getcase_tuple()
delete_category_data = OperationExcleData(excelFile, "删除配置项类型").getcase_tuple()

@pytest.mark.cmdb
@pytest.mark.run(order=1)
@allure.feature("CMDB")
@allure.story("创建配置项类型")
@pytest.mark.parametrize("ID, testcases, name, code, sourceCategoryCode, parentCategoryKey, icon, status_code, expected_result", category_data)
def test_create_category(uri, headers, ID, testcases, name, code, sourceCategoryCode, parentCategoryKey, icon,status_code, expected_result):
    """
    创建一级、二级配置项类型
    :param uri:
    :param headers:
    :param ID:
    :param testcases:
    :param name:
    :param code:
    :param sourceCategoryCode:
    :param parentCategoryKey:
    :param icon:
    :return:
    """
    CategoryKey = get_categorykey(parentCategoryKey)
    category_param = {
        "category":{
            "sourceCategoryCode":"",
            "name": name,
            "code": code,
            "parentCategoryKey": CategoryKey,
            "icon": icon
        },
        "propGroups":[{
            "group": {
                "type": "tab",
                "weight": "1",
                "name": "基本信息",
                "important": "true"
            },
            "properties": [{
                "name": "名称",
                "code": "name",
                "type": "input",
                "value": "",
                "readonly": "false",
                "nullable": "false",
                "unique": "true",
                "key": "true",
                "important": "true",
                "weight": "1",
                "validateRegex": "",
                "options": [],
                "properties": {
                    "isBuildInName": "true"
                }
            },  {
                "name": "责任人",
                "code": "administrator",
                "type": "userChoice",
                "value": "",
                "readonly": "false",
                "nullable": "false",
                "unique": "true",
                "key": "false",
                "important": "false",
                "weight": "1",
                "validateRegex": "",
                "options": [],
                "properties": {
                    "isBuildInName": "true"
                }
            }]
        }]
    }
    create_category_response = requests.post(url=uri + base_category_url,
                                              json = category_param,
                                              headers=headers).json()
    allure.attach("请求响应code", str(create_category_response['status']))
    allure.attach("请求响应结果", str(create_category_response))
    my_log().info(create_category_response)
    AssertUtil().assert_code(create_category_response['status'], status_code)
    AssertUtil().assert_in_body(create_category_response['data'], expected_result)

def get_categorykey(categoryName):
    """
    查询cmdb数据库根据传入的配置项类型获取对应_key值
    :param categoryName:
    :return:
    """
    categorykey = ""
    if categoryName == None:
        return categorykey
    else:
        # 初始化Arangodb数据库对象
        categorys = get_categorys_db()
        for category in categorys:
            if category.name == categoryName:
                categorykey=category._key
                return categorykey

@pytest.mark.cmdb
@pytest.mark.run(order=10)
@allure.feature("CMDB")
@allure.story("编辑配置项类型")
@pytest.mark.parametrize("ID, testcases, categoryName,updatename, code, sourceCategoryCode, parentCategoryKey, icon,status_code, expected_result", update_category_data)
def test_update_category(uri, headers, ID, testcases, categoryName, updatename, code, sourceCategoryCode, parentCategoryKey, icon,status_code, expected_result):
    """
    编辑配置项类型
    :param uri:
    :param headers:
    :param ID:
    :param testcases:
    :param name:
    :param code:
    :param sourceCategoryCode:
    :param parentCategoryKey:
    :param icon:
    :return:
    """
    CategoryKey = get_categorykey(categoryName)
    parentCategory = get_categorykey(parentCategoryKey)
    update_category_param = {
        "sourceCategoryCode": "",
        "name": updatename,
        "code": code,
        "parentCategoryKey": parentCategory,
        "icon": icon,
        "_key": CategoryKey,
        "deleted": "false",
        "extras": {},
        "builtIn": "false"
    }
    update_category_response = requests.put(url = uri + base_category_url + "/" + CategoryKey,
                                            headers = headers,
                                            json = update_category_param).json()
    allure.attach("请求响应code", str(update_category_response['status']))
    allure.attach("请求响应结果", str(update_category_response))
    my_log().info(update_category_response)
    AssertUtil().assert_code(update_category_response['status'], status_code)
    AssertUtil().assert_in_body(update_category_response['data'],expected_result)

@pytest.mark.cmdb
@pytest.mark.run(order=11)
@allure.feature("CMDB")
@allure.story("删除配置项类型")
@pytest.mark.parametrize("ID, testcases, name, status_code", delete_category_data)
def test_delete_category(uri, headers, ID, testcases, name, status_code):
    """
    删除配置项类型
    :param uri:
    :param headers:
    :param ID:
    :param testcases:
    :param name:
    :return:
    """
    CategoryKey = get_categorykey(name)
    delete_category_response = requests.delete(url = uri + base_category_url + "/" + CategoryKey,
                                               headers = headers).json()
    allure.attach("请求响应code", str(delete_category_response['status']))
    allure.attach("请求响应结果", str(delete_category_response))
    my_log().info(delete_category_response)
    AssertUtil().assert_code(delete_category_response['status'], status_code)
    assert name not in get_categorys_db()

def get_category_code(categoryName):
    """
    查询cmdb数据库根据传入的配置项类型获取对应code值
    :param categoryName:
    :return:
    """
    categorys = get_categorys_db()
    for category in categorys:
        if category.name == categoryName:
            category_code = category.code
            return category_code

def get_categorys_db():
    """
    获取所有配置项类型
    :return:
    """
    # 初始化Arangodb数据库对象
    conn = init_arangodb("cmdb_db")
    arangodb = conn.opendb("cmdb")
    aql = "FOR c IN category RETURN c"
    categorys = arangodb.AQLQuery(aql)
    return categorys






