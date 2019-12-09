import pytest
import requests
import json
import pymysql
import os
from config import Conf
from common.get_excel_data import OperationExcleData
from common.get_excel import read_excel_tuple

create_tenant_url="/admin/v1/vdcs/"
update_tenant_url="/admin/v1/vdcs/"
delete_tenant_url="/admin/v1/vdcs/"
manage_tenant_url="/admin/v1/vdcs/"
create_project_url="/admin/v1/projects"
update_project_url="/admin/v1/projects/"
delete_project_url="/admin/v1/projects/"

testdata_path = Conf.get_testdata_path()
excelFile = testdata_path + os.sep + "业务管理.xlsx"

create_tenant_data=OperationExcleData(excelFile,"创建租户").getCaseList()
update_tenant_data=OperationExcleData(excelFile,"编辑租户").getCaseList()
manage_user_data=OperationExcleData(excelFile,"成员管理").getCaseList()
create_project_data = read_excel_tuple(excelFile, '创建项目')
update_project_data=read_excel_tuple(excelFile, '编辑项目')


# 创建租户
@pytest.mark.run(order=8)
@pytest.mark.parametrize("create_tenant_data",create_tenant_data)
def test_create_tenant(uri, headers, create_tenant_data):
    createTenant_response = requests.post(url=uri + create_tenant_url,
                                         data=json.dumps(create_tenant_data),
                                         headers=headers)
    code = createTenant_response.status_code
    assert code == 200

#查询租户id
def get_tenant_id(uri, headers, tenantname):
    """
    根据传入的租户名称获取租户id
    :param uri:
    :param headers:
    :param tenantname:租户名称
    :return:
    """
    get_tenant_response = requests.get(url = uri + create_tenant_url,
                                       headers = headers
                                       ).json()
    for tenant in get_tenant_response['data']:
        if tenant['name'] == tenantname:
            return tenant['id']


#编辑租户
# @pytest.mark.parametrize("update_tenant_data",update_tenant_data)
# def test_update_tenant(ip,port,headers,update_tenant_data):
#     ip_address="http://%s:%s" % (ip,port)
#     tenant_id = get_tenant_id(create_tenant_data)
#     updateTenant_response=requests.post(url=ip_address+update_tenant_url+str(tenant_id[0][0]),
#                                         data=json.dumps(update_tenant_data),
#                                         headers=headers).json()
#     code = updateTenant_response['status']
#     assert code == 200

#成员管理
# @pytest.mark.parametrize("manage_user_data",manage_user_data)
# def test_manage_user(ip,port,headers,manage_user_data):
#     ip_address="http://%s:%s" % (ip,port)
#     tenant_id = get_tenant_id(update_tenant_data)
#     user_data=[]
#     user_data.append(manage_user_data)#列表嵌套字典
#     manage_user_response=requests.post(url=ip_address+manage_tenant_url+str(tenant_id[0][0])+"/users",
#                                         data=json.dumps(user_data),
#                                         headers=headers).json()
#     code = manage_user_response['status']
#     assert code == 200

# 创建项目
@pytest.mark.run(order=9)
@pytest.mark.parametrize("tenantname, projectname, description", create_project_data)
def test_create_project(uri, headers, tenantname, projectname, description):
    tenant_id = get_tenant_id(uri, headers, tenantname)
    create_project_data_param={
            "name":projectname,
            "description":description,
            "vdc":tenant_id
        }

    createProject_response = requests.post(url=uri + create_project_url,
                                         data=json.dumps(create_project_data_param),
                                         headers=headers).json()
    code = createProject_response['status']
    assert code == 200


def get_project_id(uri, headers, projectname):
    """
    根据传入的项目名称获取项目id
    :param uri:
    :param headers:
    :param projectname:项目名称
    :return:
    """
    get_project_response = requests.get(url = uri + create_project_url,
                                        headers = headers).json()
    for project in get_project_response['data']['list']:
        if project['name'] == projectname:
            return project['id']


# #编辑项目
# @pytest.mark.parametrize("name,description",update_project_data)
# def test_update_project(ip,port,headers,name,description):
#     ip_address="http://%s:%s" % (ip,port)
#     project_id = get_project_id(create_project_data[0][0])
#     update_project_data_param={
#             "name":name,
#             "description":description,
#         }
#     updateProject_response = requests.post(url=ip_address + update_project_url+str(project_id[0][0]),
#                                          data=json.dumps(update_project_data_param),
#                                          headers=headers).json()
#     code = updateProject_response['status']
#     assert code == 200
#
# #删除项目
# def test_delete_project(ip, port, headers):
#     ip_address = 'http://%s:%s' % (ip, port)
#     project_id = get_project_id(update_project_data[0][0])
#     delete_project_response = requests.delete(
#         url=ip_address + delete_project_url + str(project_id[0][0]),
#         headers=headers
#     ).json()
#     code = delete_project_response["status"]
#     assert code == 200
#
#
# #删除租户
# # @pytest.mark.parametrize("delete_tenant_data",delete_tenant_data)
# def test_delete_tenant(uri, headers):
#     tenant_id=get_tenant_id(update_tenant_data)
#     delete_tenant_response = requests.delete(
#         url=uri + delete_tenant_url + str(tenant_id[0][0]),
#         headers=headers
#     ).json()
#     code = delete_tenant_response["status"]
#     assert code == 200
#
#

