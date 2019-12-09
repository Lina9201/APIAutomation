# -*- coding: utf-8 -*-
# @Time    : 2019/12/2 9:57
# @Author  : zhuxuefei
from config import Conf
import os
import pytest
import json
import requests
from common.get_excel_data import OperationExcleData
from test_case.cmp_compute.test_resourcepool import get_resourcepoolid
from test_case.cmp_compute.test_images import get_image_id
from test_case.cmp_compute.test_datacenter import get_datacenterid
from test_case.business_management.test_tenant import get_tenant_id, get_project_id
from test_case.network_resource.test_network import get_network_id, get_subnet_id, get_subnetip_id,get_object_id


# 创建虚拟机请求url
create_instance_url = "/admin/v1/instances"

# 获取创建实例请求参数数据
testdata_path = Conf.get_testdata_path()
excelFile = testdata_path + os.sep + "物理资源.xlsx"
sheetName = "创建虚拟机"
instance_data = OperationExcleData(excelFile, sheetName).getcase_tuple()

@pytest.mark.run(order=10)
@pytest.mark.parametrize("resourcepooltype,region,resourcepool,tenant,project,vmname,account,image, ostype,cpu,memory,osdisk,disktype,net,subnet,nettype,ipaddress", instance_data)
def test_create_vm(uri, headers, resourcepooltype,region,resourcepool, tenant, project, vmname,
            account,image, ostype, cpu,memory,osdisk,disktype,net,subnet,nettype,ipaddress):


		resourcePoolId = get_resourcepoolid(uri, headers, resourcepool)
		tenantId = get_tenant_id(uri, headers, tenant)
		projectId = get_project_id(uri, headers, project)
		netId = get_network_id(uri, headers, net)
		subnetId = get_subnet_id(uri, headers, net, subnet)
		imageId = get_image_id(uri, headers,image)
		subnetipId = get_subnetip_id(uri, headers, net, subnet, ipaddress)
		objectId = get_object_id(uri, headers, resourcepool, net)

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
				"targetId": objectId,
				"extra": {}
			 }]
		}]


		create_vm_response = requests.post(url = uri + create_instance_url,
										   headers = headers,
										   data=json.dumps(create_instance_data)).json()
		assert create_vm_response['status'] == 200
