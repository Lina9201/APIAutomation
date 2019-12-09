import pytest
import requests
from common.get_excel import read_excel, read_excel_tuple
from config import Conf
from test_case.cmp_compute.test_resourcepool import get_resourcepoolid
import os
import urllib.parse


## 创建VLAN池
create_vlanpool_url_path = '/admin/v1/vlan_pools/'
## 获取VLAN池
get_vlanpool_url_path = '/admin/v1/vlan_pools/page?tag=TRADITIONAL_VLAN'
## 获取VLAN
get_vlan_url_path = '/admin/v1/vlans'
## 编辑VLAN池
update_vlanpool_url_path = '/admin/v1/vlan_pools/'
## 删除VLAN池
delete_vlanpool_url_path = '/admin/v1/vlan_pools/'

# 构造测试数据
testdata_path = Conf.get_testdata_path()
excelFile = testdata_path + os.sep + "网络资源.xlsx"
## 创建VLAN池
param_create_vlanpool = read_excel_tuple(excelFile, '创建VLAN池')
## 编辑VLAN池
param_update_vlanpool = read_excel_tuple(excelFile, '编辑VLAN池')
## 删除VLAN池
param_delete_vlanpool = read_excel(excelFile, '删除VLAN池', 'name')

# 定义函数
## 获取VLAN池列表
def get_vlanpool_list(uri, headers):
    vlanpool_list_response = requests.get(
        url=uri + get_vlanpool_url_path,
        headers=headers
    ).json()
    vlanpool_list = vlanpool_list_response['data']['list']
    return vlanpool_list


## 获取VLAN池名称
def get_vlanpool_name_list(uri, headers):
    vlanpool_name_list = []
    for i in get_vlanpool_list(uri, headers):
        vlanpool_name_list.append(i['name'])
    return vlanpool_name_list


## 获取VLAN池ID
def get_vlanpool_id(uri, headers, name):
    for i in get_vlanpool_list(uri, headers):
        if name == i['name']:
            return i['id']


def get_vlan_id(uri, headers, vlanpoolId):
    vlan_list = []
    url_data = {
        'vlanpoolId': vlanpoolId,
        'status' : "NOT_USED"
    }
    query_vlans = urllib.parse.urlencode(url_data)
    vlanIdResponse = requests.get(
        url=uri + get_vlan_url_path + "?" + query_vlans,
        headers=headers
    ).json()
    for vlan in vlanIdResponse['data']:
        if vlanpoolId == vlan['vlanPoolId']:
             vlan_list.append(vlan['id'])
    return vlan_list

# 测试用例
## 创建VLAN池
@pytest.mark.run(order=4)
@pytest.mark.parametrize('name,tag,ResourcePoolName,vlanTagStart,vlanTagEnd', param_create_vlanpool)
def test_create_vlanpool(uri, headers, name, tag, ResourcePoolName, vlanTagStart, vlanTagEnd):
    resourcepoolid = get_resourcepoolid(uri, headers, ResourcePoolName)
    param = {
        'name': name,  # VLAN池名称
        'tag': tag,
        'vlanPoolResourcePoolList': [{'resourcePoolId': resourcepoolid}],  # [{'resourcePoolId': 114}],  # 作用域调用资源池ID
        'vlanTagEnd': vlanTagStart,  # 结束VLAN ID
        'vlanTagStart': vlanTagEnd  # 起始VLAN ID
    }
    create_vlanpool_response = requests.post(
        url=uri + create_vlanpool_url_path,
        headers=headers,
        json=param
    ).json()
    print(create_vlanpool_response)
    code = create_vlanpool_response['status']
    assert code == 200

