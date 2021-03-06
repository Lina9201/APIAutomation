# -*- coding: utf-8 -*-
# @Time    : 2019/12/2 9:57
# @Author  : zhuxuefei
from config import Conf
import os
import pytest
import json
import requests
import urllib.parse
from common.get_excel_data import OperationExcleData
from common.get_db_data import init_mysqldb,assert_mysqldb
from test_case.cmp_compute.test_resourcepool import get_resourcepoolid
from test_case.cmp_compute.test_images import get_image_id
from test_case.cmp_compute.test_datacenter import get_datacenterid
from test_case.business_management.test_tenant import get_tenant_id, get_project_id
from test_case.network_resource.test_network import get_network_id, get_subnet_id, get_subnetip_id,get_object_id
import time
import allure
from utils.LogUtil import my_log
from utils.AssertUtil import AssertUtil

# 创建虚拟机请求url
create_instance_url = "/admin/v1/instances"
# 获取资源池集群url
get_cluster_url = "/admin/v1/hypersivor/vmware/clusters/?resourcePoolId="

# 获取创建实例请求参数数据
testdata_path = Conf.get_testdata_path()
excelFile = testdata_path + os.sep + "物理资源.xlsx"
sheetName = "创建虚拟机"
instance_data = OperationExcleData(excelFile, sheetName).getcase_tuple()

@pytest.mark.smoke
@pytest.mark.run(order=12)
@pytest.mark.parametrize("resourcepooltype,region,resourcepool,tenant,project,vmname,account,image, ostype,cluster,host,cpu,memory,osdisk,disktype,net,subnet,nettype,ipaddress,status_code,expected_result,expected_db", instance_data)
@allure.feature("虚拟机")
@allure.story("创建虚拟机")
def test_create_vm(uri, headers, resourcepooltype,region,resourcepool, tenant, project, vmname,
            account,image, ostype,cluster,host,cpu,memory,osdisk,disktype,net,subnet,nettype,ipaddress,status_code,expected_result,expected_db):
            resourcePoolId = get_resourcepoolid(uri, headers, resourcepool)
            tenantId = get_tenant_id(uri, headers, tenant)
            projectId = get_project_id(uri, headers, project)
            netId = get_network_id(uri, headers, net)
            subnetId = get_subnet_id(uri, headers, net, subnet)
            imageId = get_image_id(uri, headers,image)
            subnetipId = get_subnetip_id(uri, headers, net, subnet, ipaddress)
            objectId = get_object_id(uri, headers, resourcepool, net)
            global targetId
            if resourcepooltype == "vmware":
                targetId = objectId
            elif resourcepooltype == "openstack":
                targetId = netId

            create_instance_data = [{
                "count": account,
                "regionId": get_datacenterid(uri, headers, region),
                "resourcePoolId": resourcePoolId,
                "vdcId": tenantId,
                "projectId": projectId,
                "hypervisorType": resourcepooltype,
                "name": vmname,
                "description": "",
                "imageId": imageId,
                "osType": ostype,
                "cpu": cpu,
                "memory": memory,
                "osDatastore": "",
                "disks": [{
                    "name": "系统盘",
                    "os": "true",
                    "size": osdisk,
                    "type": ostype,
                    "configs": {
                        "datastore": ""
                    }
                }],
                "nics": [{
                    "name": net,
                    "networkId": netId,
                    "subnetId": subnetId,
                    "ipId": subnetipId,
                    "ip": ipaddress,
                    "type": nettype,
                    "targetId": targetId,
                    "extra": {}
                 }],
                "placement":{
                    "cluster": cluster,
                    "host": host
                }
            }]


            create_vm_response = requests.post(url = uri + create_instance_url,
                                               headers = headers,
                                               data=json.dumps(create_instance_data)).json()
            allure.attach("请求响应code", str(create_vm_response['status']))
            allure.attach("请求响应结果", str(create_vm_response))
            my_log().info(create_vm_response)
            AssertUtil().assert_code(create_vm_response['status'], status_code)
            time.sleep(120)
            AssertUtil().assert_in_body(create_vm_response['data'], expected_result)
            assert_mysqldb(get_instance_db(vmname), expected_db)


#根据虚拟机名称获取虚拟机id
def get_instance_id(uri, headers, instance_name,resourcepool):
        resourcePoolId = get_resourcepoolid(uri, headers, resourcepool)
        url_data={
            "resourcePoolId" : resourcePoolId,
            "start" : 0,
            "limit" : 100
        }
        query_vms = urllib.parse.urlencode(url_data)
        get_instance_response = requests.get(url = uri + create_instance_url+"?" + query_vms,
                                             headers = headers).json()
        for instance in get_instance_response["data"]["list"]:
            if instance["name"] == instance_name:
                return instance["id"]


#根据虚拟机名称获取虚拟机电源状态
def get_instance_powerStatus(uri, headers, instance_name,resourcepool):
        resourcePoolId = get_resourcepoolid(uri, headers, resourcepool)
        url_data={
            "resourcePoolId" : resourcePoolId,
            "start" : 0,
            "limit" : 100
        }
        query_vms = urllib.parse.urlencode(url_data)
        get_instance_response = requests.get(url = uri + create_instance_url+"?" + query_vms,
                                             headers = headers).json()
        for instance in get_instance_response["data"]["list"]:
            if instance["name"] == instance_name:
                return instance["powerStatus"]

#根据虚拟机名称获取虚拟机标识
def get_instance_vmName(uri, headers, instance_name, resourcepool):
        resourcePoolId = get_resourcepoolid(uri, headers, resourcepool)
        url_data = {
            "resourcePoolId": resourcePoolId,
            "start": 0,
            "limit": 100
        }
        query_vms = urllib.parse.urlencode(url_data)
        get_instance_response = requests.get(url=uri + create_instance_url + "?" + query_vms,
                                             headers=headers).json()
        for instance in get_instance_response["data"]["list"]:
            if instance["name"] == instance_name:
                return instance["vmName"]

#根据虚拟机名称获取虚拟机第一块网卡信息
def get_intance_nics(uri, headers, instance_name, resourcepool):
        instance_id = get_instance_id(uri, headers, instance_name, resourcepool)
        instance_url = create_instance_url + "/" + str(instance_id)
        get_instance_response = requests.get(url= uri + instance_url,
                                             headers = headers).json()
        return get_instance_response["data"]["nicInfos"][0]

#根据虚拟机名称获取虚拟机系统盘信息
def get_instance_disks(uri, headers, instance_name, resourcepool):
        instance_id = get_instance_id(uri, headers, instance_name, resourcepool)
        instance_url = create_instance_url + "/" + str(instance_id)
        get_instance_response = requests.get(url= uri + instance_url,
                                             headers = headers).json()
        for disk in get_instance_response["data"]["disks"]:
            if disk["name"] == "系统盘":
                return disk

def get_instance_db(vmname):
    """
    查询instance表
    :param vmname:
    :return:
    """
    sql = init_mysqldb("tcrc_db")
    try:
        db_res = sql.fetchone("select * from cmp_compute.instance where name='%s'" % vmname)
        return db_res
    except:
        my_log("cmp_compute_instance").error("%s名称虚拟机不存在" % vmname)



