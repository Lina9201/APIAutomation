import requests
import pytest
from config import Conf
import os
from common.get_excel import read_excel, read_excel_tuple
from test_case.cmp_compute.test_resourcepool import get_resourcepoolid

# 创建镜像
create_images_url = "/admin/v1/images?osType="
# 获取vmware模板
get_vmware_templates_url = "/admin/v1/hypersivor/vmware/templates?resourcePoolId="
# 获取openstack模板
get_openstack_templates_url = "/admin/v1/hypersivor/openstack/images?resourcePoolId="
# 获取镜像
get_images_url = "/admin/v1/images/"
# 构造测试数据
# 构造测试数据
testdata_path = Conf.get_testdata_path()
excelFile = testdata_path + os.sep + "镜像管理.xlsx"
# 创建镜像
param_create_images = read_excel_tuple(excelFile, '创建镜像')
# 编辑镜像
param_update_images = read_excel_tuple(excelFile, '编辑镜像')
# 删除镜像
param_delete_images = read_excel(excelFile, '删除镜像', 'image_name')
# 添加资源池模板
param_create_template = read_excel_tuple(excelFile, '添加资源池模板')
# 编辑资源池模板
param_update_template = read_excel_tuple(excelFile, '编辑资源池模板')


# 根据传入的资源池获取镜像模板列表
def get_template_list(uri, headers, resourcepoolType, resourcepoolName):
    template_list = []
    resourcepool_id = get_resourcepoolid(uri, headers,  resourcepoolName)
    if resourcepoolType == "vmware":
        get_vmware_template_response = requests.get(url=uri + get_vmware_templates_url + str(resourcepool_id),
                                        headers=headers).json()
        template_list = get_vmware_template_response['data']
    elif resourcepoolType == "openstack":
        get_openstack_template_response = requests.get(url=uri + get_openstack_templates_url + str(resourcepool_id),
                                                       headers=headers).json()
        template_list = get_openstack_template_response['data']
    return template_list


# 根据传入的资源池获取镜像模板列表名称
def get_template_name(uri, headers, resourcepoolType, resourcepoolName):
    template_name = []
    for template in get_template_list(uri, headers, resourcepoolType, resourcepoolName):
        template_name.append(template['name'])
    return template_name

# 根据选择的资源池名称获取资源池id
def get_template_id(uri, headers, resourcepoolType, resourcepoolName, template_name):
    for template in get_template_list(uri, headers, resourcepoolType, resourcepoolName):
        if template['name'] == template_name:
            return template['id'] or template['morValue']


# 获取镜像列表
def get_images_list(uri, headers):
    images_list_response = requests.get(
        url=uri + create_images_url,
        headers=headers
    ).json()
    images_list = images_list_response['data']
    return images_list


# 获取镜像名称列表
# def test_get_images_name_list(uri, headers):
#     images_name_list = []
#     for i in test_get_images_list(uri, headers):
#         images_name_list.append(i['name'])
#     return images_name_list


# 根据镜像名称获取镜像id
def get_image_id(uri, headers, imagename):
    for image in get_images_list(uri, headers):
        if image['name'] == imagename:
            return image['id']


## 获取编辑后的镜像ID
# def test_get_update_images_id(ip, port, headers):
#     update_images_id = []
#     for i in test_get_images_list(ip, port, headers):
#         if param_update_images[0][0] == i['name']:
#             update_images_id.append(i['id'])  # [379]
#     return update_images_id


#
# 创建镜像：操作系统为linux,操作系统版本为Centos6.5
@pytest.mark.run(order=3)
@pytest.mark.parametrize("name,description,os,osType,osDisk,password,username,loading,resourcepoolType,resourcepoolName",
                         param_create_images)
def test_create_images(uri, headers, name, description, os, osType, osDisk, password, username, loading,
                    resourcepoolName, resourcepoolType):
    template_name = get_template_name(uri, headers, resourcepoolType, resourcepoolName)[0]
    templateId = get_template_id(uri, headers, resourcepoolType, resourcepoolName, template_name)
    resourcepoolid = get_resourcepoolid(uri, headers, resourcepoolName)
    create_images_param = {"description": description,
                           "name": name,
                           "os": os,
                           "osType": osType,
                           "relations": [
                               {
                                   "extra": {
                                       "osDisk": osDisk,
                                       "password": password,
                                       "username": username
                                   },
                                   "loading": loading,
                                   "relavant": {},
                                   "relavantId": templateId[0],
                                   "relavantName": template_name,
                                   "resourcepoolId": resourcepoolid,
                                   "resourcepoolType": resourcepoolType
                               }
                           ]
                           }
    create_images_response = requests.post(url=uri + create_images_url,
                                           json=create_images_param,
                                           headers=headers).json()
    assert create_images_response["status"] == 200
    # 获取已关联的资源池模板id
    # resourcepool_template_list = test_get_resourcepool_template_list(uri, headers)
    # 断言创建的镜像名称能在查询到的响应结果中存在
    # assert name in test_get_images_name_list(uri, headers)
    # assert resourcepoolid == resourcepool_template_list[0]["resourcepoolId"]  # 返回的值是114（int）
    # assert relavantName == resourcepool_template_list[0]["relavantName"]
    # assert username == resourcepool_template_list[0]["extra"]["username"]
    # assert password == resourcepool_template_list[0]["extra"]["password"]
    # assert str(osDisk) == resourcepool_template_list[0]["extra"]["osDisk"]


# 校验创建镜像的资源池/模板/用户名/密码信息列表
# def test_get_resourcepool_template_list(ip, port, headers):
#     relation = "/relations?"
#     ip_address = 'http://%s:%s' % (ip, port)
#     image_id = test_get_images_id(ip, port, headers)[0][0]
#     get_images_param_response = requests.get(
#         url=ip_address + get_images_url + str(image_id) + relation,
#         headers=headers).json()
#     assert get_images_param_response["status"] == 200
#     return get_images_param_response["data"]


# 获取relavantName列表
# def test_get_template_name_list(ip, port, headers):
#     template_name_list = []
#     for i in test_get_resourcepool_template_list(ip, port, headers):
#         template_name_list.append(i['relavantName'])
#     return template_name_list
#

# 删除关联的vmware资源池模板
# def test_create_resourcepoll_template(ip, port, headers):
#     ip_address = "http://%s:%s" % (ip, port)
#     relation_url = "/relations"
#     image_id = test_get_images_id(ip, port, headers)[0][0]
#     delete_resourcepoll_template_param = []
#     delete_resourcepoll_template_response = requests.post(
#         url=ip_address + get_images_url + str(image_id) + relation_url,
#         json=delete_resourcepoll_template_param,
#         headers=headers).json()
#     assert delete_resourcepoll_template_response["status"] == 200
#     # 断言镜像的资源池模板为空，即无数据
#     assert "data" not in delete_resourcepoll_template_response.keys()


# 添加关联的资源池模板
# @pytest.mark.parametrize("loading,osDisk,password,username,relavantName,resourcepoolType",
#                          param_create_template)
# def test_create_resourcepoll_template(ip, port, headers, loading, osDisk, password, username, relavantName,
#                                       resourcepoolType):
#     ip_address = "http://%s:%s" % (ip, port)
#     resourcepoolid = 114
#     relavant_template_id = test_get_vmware_template_id(ip, port, headers)[0]
#     image_id = test_get_images_id(ip, port, headers)[0][0]
#     relation_url = "/relations"
#     create_resourcepoll_template_param = [
#         {"imageId": image_id,
#          "loading": loading,
#          "extra":
#              {
#                  "osDisk": osDisk,
#                  "password": password,
#                  "username": username
#              },
#          "relavant": {},
#          "relavantId": relavant_template_id,
#          "relavantName": relavantName,
#          "resourcepoolId": resourcepoolid,
#          "resourcepoolType": resourcepoolType
#          }]
#     create_resourcepoll_template_response = requests.post(
#         url=ip_address + get_images_url + str(image_id) + relation_url,
#         json=create_resourcepoll_template_param,
#         headers=headers).json()
#     assert create_resourcepoll_template_response["status"] == 200
#     # 断言创建的模板关联能在查询到的响应结果中存在
#     assert relavantName in test_get_template_name_list(ip, port, headers)


# 编辑创建时关联的资源池模板（vmware资源池修改为openstack资源池）
# @pytest.mark.parametrize("username,password,osDisk,loading,relavantName,resourcepoolName,resourcepoolType",
#                          param_update_template)
# def test_update_temlate(ip, port, headers, username, password, osDisk, loading, relavantName, resourcepoolName,
#                         resourcepoolType):
#     ip_address = "http://%s:%s" % (ip, port)
#     resourcepoolId = 116
#     relavantId = test_get_openstack_template_id(ip, port, headers)[0]
#     relation_url = "/relations"
#     image_id = test_get_images_id(ip, port, headers)[0][0]
#     update_tempalte_param = [{"extra": {
#         "osDisk": osDisk,
#         "password": password,
#         "username": username,
#     },
#         "imageId": int(image_id),
#         "loading": loading,
#         "relavantId": relavantId,
#         "relavantName": relavantName,
#         "resourcepoolId": resourcepoolId,
#         "resourcepoolName": resourcepoolName,
#         "resourcepoolType": resourcepoolType
#     }]
#     update_tempalte_response = requests.post(url=ip_address + get_images_url + str(image_id) + relation_url,
#                                              json=update_tempalte_param,
#                                              headers=headers).json()
#     assert update_tempalte_response["status"] == 200
#     # 断言创建的镜像名称能在查询到的响应结果中存在
#     assert update_tempalte_param[0]["resourcepoolId"] in test_get_resourcepool_template_id_list(ip, port, headers)[0]
#     assert update_tempalte_param[0]["relavantId"] in test_get_resourcepool_template_id_list(ip, port, headers)[1]
#

# 根据镜像名称获取关联的资源池模板列表
# def test_get_relation_template_list(ip, port, headers):
#     ip_address = "http://%s:%s" % (ip, port)
#     relation_url = "/relations"
#     image_id = test_get_images_id(ip, port, headers)[0][0]
#     get_relation_tempalte_list_response = requests.get(url=ip_address + get_images_url + str(image_id) + relation_url,
#                                                        headers=headers).json()
#     assert get_relation_tempalte_list_response["status"] == 200
#     return get_relation_tempalte_list_response["data"]  # 列表


# 根据资源池模板列表获取资源池id/模板id
# def test_get_resourcepool_template_id_list(ip, port, headers):
#     resourcepool_id_list = []
#     template_id_list = []
#     for i in test_get_relation_template_list(ip, port, headers):
#         resourcepool_id_list.append(i['resourcepoolId'])  # 返回[474]
#         template_id_list.append(i['relavantId'])  # 返回[""]
#     return resourcepool_id_list, template_id_list


# 编辑镜像
# @pytest.mark.parametrize("name,os,osType,deleted,isPublic", param_update_images)
# def test_udpate_images(ip, port, headers, name, os, osType, deleted, isPublic):
#     resourcepoolid = 114
#     ip_address = 'http://%s:%s' % (ip, port)
#     image_id = test_get_images_id(ip, port, headers)[0][0]
#     update_images_param = {"name": name,
#                            "os": os,
#                            "osType": osType,
#                            "deleted": deleted,
#                            "isPublic": isPublic
#                            }
#     update_images_param_response = requests.post(
#         url=ip_address + get_images_url + str(image_id),
#         headers=headers,
#         json=update_images_param
#     ).json()
#     assert update_images_param_response["status"] == 200
#     assert update_images_param["name"] in test_get_images_name_list(ip, port, headers)


# 删除镜像
# @pytest.mark.parametrize('image_name', param_delete_images)
# def test_delete_image(ip, port, headers, image_name):
#     ip_address = 'http://%s:%s' % (ip, port)
#     print(image_name)
#     image_id = test_get_update_images_id(ip, port, headers)[0]
#     delete_images_response = requests.delete(
#         url=ip_address + get_images_url + str(image_id),
#         headers=headers
#     ).json()
#     assert delete_images_response['status'] == 200
#     assert image_name not in test_get_images_name_list(ip, port, headers)
