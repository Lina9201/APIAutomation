import pytest
import requests
from config import Conf
import os
import urllib.parse
from common.get_excel import read_excel, read_excel_tuple
from test_case.network_resource.test_vlanpool import get_vlanpool_id
from test_case.network_resource.test_vlanpool import get_vlan_id
from test_case.cmp_compute.test_resourcepool import get_resourcepoolid

## 创建网络
create_network_url_path = '/admin/v1/networks/'
## 获取网络列表
get_network_url_path = '/admin/v1/networks/page/'
## 编辑网络
update_network_url_path = '/admin/v1/networks/'
## 创建子网
create_subnet_url_path = '/admin/v1/subnets?networkId='
## 获取子网列表
get_subnet_url_path = '/admin/v1/subnets/page?networkId='
## 获取选择网络子网下的IP列表
get_subnet_ips_url = '/admin/v1/subnet_ips'
## 编辑子网
update_subnet_url_path = '/admin/v1/subnets/'
## 删除子网
delete_subnet_url_path = '/admin/v1/subnets/'
## 创建网络对象
create_network_object_url_path = '/admin/v1/network_objects/create?networkId='
## 添加已有网络对象
add_network_object_url_path = '/admin/v1/network_objects/add?networkId='
## 获取网络所对应的资源池信息
get_network_resourcepool_url_path = '/admin/v1/networks/resource_pools/'
## 获取网络所对应的VMware资源池中的分布式交换机
get_network_dvswitch_url_path = '/admin/v1/hypersivor/vmware/dvswitches?resourcePoolId='
## 获取网络已添加对象
get_network_object_url_path = '/admin/v1/network_objects/page?networkId='
## 获取网路所对应的VMware资源池中的端口组
get_network_dvportgroup_url_path = '/admin/v1/hypersivor/vmware/dvportgroups?resourcePoolId='
## 获取网路所对应的Openstack资源池中的端口组
get_network_openstack_url_path = '/admin/v1/hypersivor/openstack/networks?resourcePoolId='
## 获取网络对象
network_object_url_path = '/admin/v1/network_objects/'
## 删除网络
delete_network_url_path = '/admin/v1/networks/'

# 获取构造测试数据
testdata_path = Conf.get_testdata_path()
excelFile = testdata_path + os.sep + "网络资源.xlsx"
## 创建网络
param_create_network = read_excel_tuple(excelFile, '创建网络')
## 编辑网络
param_update_network = read_excel_tuple(excelFile, '编辑网络')
## 创建子网
param_create_subnet = read_excel_tuple(excelFile, '创建子网')
## 编辑子网
param_update_subnet = read_excel_tuple(excelFile, '编辑子网')
## 删除子网
param_delete_subnet = read_excel_tuple(excelFile, '删除子网')
## 创建新对象
param_create_network_object = read_excel_tuple(excelFile, '创建新对象')
## 添加已有对象
param_add_network_object = read_excel_tuple(excelFile, '添加已有对象')
## 编辑对象
# param_update_network_object = read_excel_tuple(excelFile, '编辑对象')
## 删除对象
param_delete_network_object = read_excel_tuple(excelFile, '删除对象')
## 删除网络
param_delete_network = read_excel(excelFile, '删除网络', 'network_name')

## 获取子网列表
def get_subnet_list(uri, headers, network_name):
    network_id = get_network_id(uri, headers, network_name)
    subnet_list_response = requests.get(
        url=uri + get_subnet_url_path + str(network_id),
        headers=headers
    ).json()
    subnet_list = subnet_list_response['data']['list']
    return subnet_list


## 获取子网名称
def get_subnet_name_list(uri, hearders, network_name):
    subnet_name_list = []
    for i in get_subnet_list(uri, hearders, network_name):
        subnet_name_list.append(i['name'])
    return subnet_name_list


## 获取子网ID
def get_subnet_id(uri, headers, network_name, subnet_name):
    for subnet in get_subnet_list(uri, headers, network_name):
        if subnet_name == subnet['name']:
            return subnet['id']


def get_subnet_ips(uri, headers, network_name, subnet_name):
    """
    根据选择网络、子网获取IP列表
    :param uri:
    :param headers:
    :param network_name:
    :param subnet_name:
    :return:
    """
    subnetId = get_subnet_id(uri, headers, network_name, subnet_name)
    url_data = {
        'subnetId': subnetId,
        'status': "NOT_USED"
    }
    query_ips = urllib.parse.urlencode(url_data)
    get_subnetIps_response = requests.get(url = uri + get_subnet_ips_url + "?" + query_ips,
                                          headers = headers).json()
    subnet_ips_list = get_subnetIps_response['data']
    return subnet_ips_list


def get_subnetip_id(uri, headers, network_name, subnet_name, ipaddress):
    """
    根据传入的ip获取对应的id
    :param uri:
    :param headers:
    :param network_name:
    :param subnet_name:
    :param ip:
    :return:
    """
    for subnetip in get_subnet_ips(uri, headers, network_name, subnet_name):
        if subnetip['ip'] == ipaddress:
            return subnetip['id']

## 获取资源池中分布式交换机名称列表
# def get_dvswitch_name_list(uri, headers, network_name, network_resourcepool_name):
#     network_dvswitch_name_list = []
#     for i in get_dvswitch_list(uri, headers, network_name, network_resourcepool_name):
#         network_dvswitch_name_list.append(i['name'])
#     return network_dvswitch_name_list


## 获取资源池中分布式交换机id
# def get_dvswitch_id(uri, headers, network_name, network_resourcepool_name, dvswitch_name):
#     network_dvswitch_id = []
#     for i in get_dvswitch_list(uri, headers, network_name, network_resourcepool_name):
#         if dvswitch_name == i['name']:
#             network_dvswitch_id = (i['id'])
#     return network_dvswitch_id


## 根据选择的资源池、网络获取可选择的端口组id
def get_object_id(uri, headers, resourcepool, network_name):
    networkId = get_network_id(uri, headers, network_name)
    resourcepoolId = get_resourcepoolid(uri, headers, resourcepool)
    data_url = {
        "networkdId": networkId,
        "resourcePoolId": resourcepoolId
    }
    query_object = urllib.parse.urlencode(data_url)
    get_object_response = requests.get(url = uri + network_object_url_path + "?" + query_object,
                                       headers = headers).json()
    for object in get_object_response['data']:
        return object['objectId']


## 获取网络所包含资源池中的端口组列表
def get_network_dvportgroup_list(uri, headers, resourcePoolType, network_resourcepool_name):
    network_resourcepool_id = get_resourcepoolid(uri, headers, network_resourcepool_name)
    network_dvportgroup_list = []
    if resourcePoolType == "vmware":
        network_dvportgroup_response = requests.get(
            url=uri + get_network_dvportgroup_url_path + str(network_resourcepool_id),
            headers=headers
        ).json()
        network_dvportgroup_list = network_dvportgroup_response['data']
    elif resourcePoolType == "openstack":
        network_dvportgroup_response = requests.get(
            url=uri + get_network_openstack_url_path + str(network_resourcepool_id),
            headers=headers
        ).json()
        network_dvportgroup_list = network_dvportgroup_response['data']
    return network_dvportgroup_list

def get_network_dvportgroup_name_list(uri, headers, resourcePoolType, network_resourcepool_name):
    """
    获取网络所包含资源池中的端口组名称列表
    :param uri:
    :param headers:
    :param network_resourcepool_name:
    :return:
    """
    network_dvportgroup_name_list = []
    for i in get_network_dvportgroup_list(uri, headers, resourcePoolType, network_resourcepool_name):
        network_dvportgroup_name_list.append(i['name'])
    return network_dvportgroup_name_list


def get_network_dvportgroup_id(uri, headers, resourcePoolType, network_resourcepool_name, dvportgroup_name):
    """
    获取网络所包含资源池中的端口组ID
    :param uri:
    :param headers:
    :param network_resourcepool_name:
    :param dvportgroup_name:
    :return:
    """
    network_dvportgroup_id = []
    for i in get_network_dvportgroup_list(uri, headers, resourcePoolType, network_resourcepool_name):
        if dvportgroup_name == i['name']:
            if resourcePoolType == "vmware":
                network_dvportgroup_id = (i['morValue'])
            elif resourcePoolType == "openstack":
                network_dvportgroup_id = (i['id'])
    return network_dvportgroup_id


def get_network_id(uri, headers, network_name):
    """
    根据传入的网络名称获取对应的网络ID
    :param uri:
    :param headers:
    :param network_name:
    :return:
    """
    network_list_response = requests.get(url = uri + get_network_url_path, headers=headers).json()
    for network in network_list_response['data']['list']:
        if network['name'] == network_name:
            return network['id']


# 测试用例
## 创建网络
### 通过选择VLAN池创建网络
@pytest.mark.run(order=5)
@pytest.mark.parametrize('name,type,vlanPoolName,category,tagType,description', param_create_network)
def test_create_network(uri, headers, name, type, vlanPoolName, category, tagType,
                        description):
    vlanPoolId = get_vlanpool_id(uri, headers, vlanPoolName)
    vlanId = get_vlan_id(uri, headers, vlanPoolId)[0]
    param = {
        'name': name,
        'type': type,
        'category': category,
        'tagType': tagType,
        'description': description,
        'vlanId': vlanId,
        'vlanPoolId': vlanPoolId
    }
    create_network_response = requests.post(
        url = uri + create_network_url_path,
        headers = headers,
        json = param
    ).json()
    print(create_network_response)
    code = create_network_response['status']
    assert code == 200



## 添加已有对象
@pytest.mark.run(order=6)
@pytest.mark.parametrize('network_name,resourcePoolType,network_resourcepool_name', param_add_network_object)
def test_add_network_object(uri, headers, network_name,resourcePoolType, network_resourcepool_name):
    network_id = get_network_id(uri, headers, network_name)
    network_resourcepool_id = get_resourcepoolid(uri, headers, network_resourcepool_name)
    objectname = get_network_dvportgroup_name_list(uri, headers, resourcePoolType, network_resourcepool_name)[0]
    objectId = get_network_dvportgroup_id(uri, headers, resourcePoolType, network_resourcepool_name, objectname)
    param = [{
        'objectId': objectId,
        'objectName': objectname,
        'resourcePoolId': network_resourcepool_id,
        'resourcePoolType': resourcePoolType,
        'vlanPoolResourcePoolId': network_resourcepool_id
    }]
    add_network_object_response = requests.post(
        url=uri + add_network_object_url_path + str(network_id),
        headers=headers,
        json=param
    ).json()
    code = add_network_object_response['status']
    # assert code == 200



## 编辑网络对象
# @pytest.mark.parametrize('network_name,network_resourcepool_name,object_name,updata_object_name', param_update_network_object)
# def test_update_network_object(ip,port,headers,network_name,network_resourcepool_name,object_name,updata_object_name):
#     ip_address = 'http://%s:%s' % (ip, port)
#     network_object_id = get_object_id(ip, port, headers, network_name, object_name)[0]
#     network_id =get_network_id(ip,port,headers,network_name)[0]
#     object_id = get_network_dvportgroup_id(ip, port, headers, network_name, network_resourcepool_name, updata_object_name)
#     resourcePoolId = get_network_resourcepool_id(ip,port,headers,network_name,network_resourcepool_name)[0]
#     param = {
#         'id':  network_object_id,
#         'networkId': network_id,
#         'objectId': object_id,
#         'objectName': updata_object_name,
#         'objectType': "DistributePortGroup",
#         'resourcePoolId': resourcePoolId,
#         'resourcePoolName': network_resourcepool_name,
#         'resourcePoolType': 'vmware'
#     }
#     update_network_object_response =requests.put(
#         url=ip_address + update_network_object_url_path+str(network_object_id)+'?networkId='+str(network_id),
#         headers=headers,
#         json=param
#     ).json()
#     code = update_network_object_response['status']
#     assert code == 200
#     assert updata_object_name in get_object_name_list(ip,port,headers,network_name)

## 删除网络对象
# @pytest.mark.parametrize('network_name,object_name', param_delete_network_object)
# def test_delete_network_object(ip, port, headers, network_name, object_name):
#     ip_address = 'http://%s:%s' % (ip, port)
#     object_id = get_object_id(ip, port, headers, network_name, object_name)[0]
#     delete_network_object_response = requests.delete(
#         url=ip_address + delete_network_object_url_path + str(object_id),
#         headers=headers
#     ).json()


@pytest.mark.run(order=7)
@pytest.mark.parametrize(
    'network_name,subnet_name,ipProtocol,cidr,isGatewayDisabled,gatewayIp,ipPools,preferredDns,alternateDns',
    param_create_subnet)
def test_create_subnet(uri, headers, network_name, subnet_name, ipProtocol, cidr, isGatewayDisabled, gatewayIp,
                       ipPools, preferredDns, alternateDns):
    """
    给选择的网络添加子网
    :param uri:
    :param headers:
    :param network_name:
    :param subnet_name:
    :param ipProtocol:
    :param cidr:
    :param isGatewayDisabled:
    :param gatewayIp:
    :param ipPools:
    :param preferredDns:
    :param alternateDns:
    :return:
    """
    network_id = get_network_id(uri, headers, network_name)
    param = {
        'name': subnet_name,
        'ipProtocol': ipProtocol,
        'cidr': cidr,
        'isGatewayDisabled': isGatewayDisabled,
        'gatewayIp': gatewayIp,
        'ipPools': ipPools,
        'preferredDns': preferredDns,
        'alternateDns': alternateDns
    }
    create_subnet_response = requests.post(
        url=uri + create_subnet_url_path + str(network_id),
        headers=headers,
        json=param
    ).json()
    code = create_subnet_response['status']
    assert code == 200
    assert subnet_name in get_subnet_name_list(uri, headers, network_name)

