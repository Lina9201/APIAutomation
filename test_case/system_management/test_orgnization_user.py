import requests
import pytest
import json
from common.get_excel import read_excel, read_excel_tuple
from common.get_excel_data import OperationExcleData

# 创建2个组织，在组织1下创建用户1，在组织2下添加已有用户，移除用户，在组织1下删除用户，编辑组织，删除组织
# 创建组织url
create_orgnization_url = "/admin/v1/organizations"
# 编辑组织/删除组织url
update_orgnization_url = "/admin/v1/organizations/"
# 创建用户url
create_user_url = "/admin/v1/users"
# 编辑/删除用户url
update_user_url = "/admin/v1/users/"

# 测试数据
# 创建组织
create_orgnization_param = OperationExcleData('../../test_data/组织用户.xlsx', '创建组织').getCaseList(
    '../../test_data/组织用户.xlsx', '创建组织')
# 编辑组织
update_orgnization_param = OperationExcleData('../../test_data/组织用户.xlsx', '编辑组织').getCaseList(
    '../../test_data/组织用户.xlsx', '编辑组织')
# 删除组织
delete_orgnization_param = OperationExcleData('../../test_data/组织用户.xlsx', '删除组织').getCaseList(
    '../../test_data/组织用户.xlsx', '删除组织')

# 创建用户
create_user_param = read_excel_tuple('../../test_data/组织用户.xlsx', '创建用户')
# 编辑用户
update_user_param = read_excel_tuple('../../test_data/组织用户.xlsx', '编辑用户')
# 修改密码
update_user_password = read_excel('../../test_data/组织用户.xlsx', '修改密码', 'password')


# 获取组织列表
def test_get_orgnization_list(ip, port, headers):
    ip_address = 'http://%s:%s' % (ip, port)
    orgnization_list_response = requests.get(
        url=ip_address + create_orgnization_url,
        headers=headers
    ).json()
    orgnization_list = orgnization_list_response['data']
    return orgnization_list


# 获取组织名称列表
def test_get_orgnization_name_list(ip, port, headers):
    orgnization_name_list = []
    for i in test_get_orgnization_list(ip, port, headers):
        orgnization_name_list.append(i['alias'])
    return orgnization_name_list


# 获取创建的组织test_org的ID
def test_get_create_orgnization_id(ip, port, headers):
    orgnization_id = []
    for i in test_get_orgnization_list(ip, port, headers):
        if create_orgnization_param[0]["name"] == i['alias']:
            orgnization_id.append(i['id'])
    print(orgnization_id)
    return orgnization_id


# 获取创建的组织test_org2的ID
def test_get_create_orgnization_org2_id(ip, port, headers):
    orgnization_id = []
    for i in test_get_orgnization_list(ip, port, headers):
        if create_orgnization_param[1]["name"] == i['alias']:
            orgnization_id.append(i['id'])
    print(orgnization_id)
    return orgnization_id


## 获取编辑后的组织ID
def test_get_update_orgnization_id(ip, port, headers):
    update_orgnization_id = []
    for i in test_get_orgnization_list(ip, port, headers):
        if update_orgnization_param[0]["name"] == i['alias']:
            update_orgnization_id.append(i['id'])
    return update_orgnization_id


# 创建组织
@pytest.mark.parametrize('create_orgnization_param', create_orgnization_param)
def test_create_orgnization(ip, port, headers, create_orgnization_param):
    ip_address = "http://%s:%s" % (ip, port)
    create_orgnization_response = requests.post(
        url=ip_address + create_orgnization_url,
        headers=headers,
        data=json.dumps(create_orgnization_param)
    ).json()
    assert create_orgnization_response['status'] == 200
    assert create_orgnization_param["name"] in test_get_orgnization_name_list(ip, port, headers)


# 在组织test_org下创建用户
@pytest.mark.parametrize('account,password,name,status,mobilePhone,birstday,sex,isManager,roles', create_user_param)
def test_create_user(ip, port, headers, account, password, name, status, mobilePhone, birstday, sex, isManager, roles):
    ip_address = "http://%s:%s" % (ip, port)
    orgnization_id = test_get_create_orgnization_id(ip, port, headers)
    roled = json.loads(roles)
    create_param = {
        "account": account,
        "password": password,
        "name": name,
        "mobilePhone": mobilePhone,
        "extra": {
            "birstday": birstday,
            "sex": sex,
            "isManager": isManager
        },
        "organizations": orgnization_id,
        "roles": roled,
        "status": status,
    }
    create_user_response = requests.post(
        url=ip_address + create_user_url,
        headers=headers,
        json=create_param
    ).json()
    assert create_user_response['status'] == 200
    assert create_param["account"] in test_get_user_account_list(ip, port, headers)[0]
    assert create_param["name"] in test_get_user_account_list(ip, port, headers)[1]
    # 创建时的值为["ROLE_XTGLY", "ROLE_YWGLY", "ROLE_YYGLY", "ROLE_ZH", "ROLE_ZHGLY"]，检查的值为["ROLE_YYGLY","ROLE_ZH","ROLE_XTGLY","ROLE_ZHGLY","ROLE_YWGLY"]
    assert create_param["roles"].sort() == test_get_user_roles_id(ip, port, headers).sort()


# 在组织test_org2下添加已有用户,便于移除用户
def test_create_existing_user(ip, port, headers):
    ip_address = "http://%s:%s" % (ip, port)
    users_id = test_get_user_account_list(ip, port, headers)[2][0]
    org_url = "/organizations"
    orgnization_org_id = test_get_create_orgnization_id(ip, port, headers)
    orgnization_org2_id = test_get_create_orgnization_org2_id(ip, port, headers)
    # 传入的参数第一个是已有用户的组织id,第二个是正在添加已有用户的组织
    create_existing_param = [orgnization_org_id[0], orgnization_org2_id[0]]
    create_existing_response = requests.post(
        url=ip_address + update_user_url + users_id + org_url,
        headers=headers,
        json=create_existing_param
    ).json()
    assert create_existing_response['status'] == 200


# 在组织test_org2下移除用户
def test_remove_existing_user(ip, port, headers):
    ip_address = "http://%s:%s" % (ip, port)
    users_id = test_get_user_account_list(ip, port, headers)[2][0]
    users_url = "/users/"
    orgnization_org2_id = test_get_create_orgnization_org2_id(ip, port, headers)[0]
    remove_existing_user_response = requests.delete(
        url=ip_address + update_orgnization_url + orgnization_org2_id + users_url + users_id,
        headers=headers
    ).json()
    assert remove_existing_user_response['status'] == 200


# 获取创建组织1下的用户列表
def test_get_fixed_user_list(ip, port, headers):
    ip_address = 'http://%s:%s' % (ip, port)
    user_url = "/users"
    fixed_orgnization_id = test_get_create_orgnization_id(ip, port, headers)
    fixed_orgnization_list_response = requests.get(
        url=ip_address + update_orgnization_url + fixed_orgnization_id[0] + user_url,
        headers=headers
    ).json()
    assert fixed_orgnization_list_response["status"] == 200
    fixed_orgnization_list = fixed_orgnization_list_response['data']
    return fixed_orgnization_list


# 获取创建组织2下的用户列表
def test_get_fixed_org2_user_list(ip, port, headers):
    ip_address = 'http://%s:%s' % (ip, port)
    user_url = "/users"
    fixed_orgnization_id = test_get_create_orgnization_org2_id(ip, port, headers)
    fixed_orgnization_user_list_response = requests.get(
        url=ip_address + update_orgnization_url + fixed_orgnization_id[0] + user_url,
        headers=headers
    ).json()
    assert fixed_orgnization_user_list_response["status"] == 200
    fixed_orgnization_user_list = fixed_orgnization_user_list_response['data']
    return fixed_orgnization_user_list


# 获取组织1下的用户名/姓名/id
def test_get_user_account_list(ip, port, headers):
    account_list = []
    name_list = []
    id_list = []
    for i in test_get_fixed_user_list(ip, port, headers):
        account_list.append(i['account'])
        name_list.append(i['name'])
        id_list.append(i['id'])
    print(account_list)
    print(name_list)
    print(id_list)
    # 返回元组([""],[""],[""])
    return account_list, name_list, id_list


# 获取组织org2下的用户名/姓名/id
def test_get_org2_user_account_list(ip, port, headers):
    account_list = []
    name_list = []
    id_list = []
    for i in test_get_fixed_org2_user_list(ip, port, headers):
        account_list.append(i['account'])
        name_list.append(i['name'])
        id_list.append(i['id'])
    print(account_list)
    print(name_list)
    print(id_list)
    # 返回元组([""],[""],[""])
    return account_list, name_list, id_list


# 获取用户的角色
def test_get_user_roles_id(ip, port, headers):
    ip_address = 'http://%s:%s' % (ip, port)
    get_roles_url = "/roles"
    user_role_id = []
    user_id = test_get_user_account_list(ip, port, headers)[2]
    get_roles_list_response = requests.get(
        url=ip_address + update_user_url + user_id[0] + get_roles_url,
        headers=headers
    ).json()
    assert get_roles_list_response["status"] == 200
    for i in get_roles_list_response["data"]:
        user_role_id.append(i['id'])
    print(user_role_id)
    return user_role_id


# 修改密码
@pytest.mark.parametrize('password', update_user_password)
def test_update_password(ip, port, headers, password):
    ip_address = 'http://%s:%s' % (ip, port)
    users_id = test_get_user_account_list(ip, port, headers)[2][0]
    password_url = "/password"
    update_password_param = {"password": password
                             }
    update_user_password_response = requests.post(
        url=ip_address + update_user_url + users_id + password_url,
        headers=headers,
        json=update_password_param
    ).json()
    assert update_user_password_response['status'] == 200


# 编辑test_org组织下的用户
@pytest.mark.parametrize('account,name,status,mobilePhone,birstday,sex,isManager,roles', update_user_param)
def test_udpate_user(ip, port, headers, account, name, status, mobilePhone, birstday, sex, isManager, roles):
    ip_address = "http://%s:%s" % (ip, port)
    users_id = test_get_user_account_list(ip, port, headers)[2][0]
    roled = json.loads(roles)
    update_user_param = {
        "account": account,
        "name": name,
        "mobilePhone": mobilePhone,
        "extra": {
            "birstday": birstday,
            "sex": sex,
            "isManager": isManager
        },
        "roles": roled,
        "status": status,
    }
    udpate_user_response = requests.post(
        url=ip_address + update_user_url + users_id,
        headers=headers,
        json=update_user_param
    ).json()
    assert udpate_user_response['status'] == 200
    assert update_user_param["account"] in test_get_user_account_list(ip, port, headers)[0]
    assert update_user_param["name"] in test_get_user_account_list(ip, port, headers)[1]
    # 创建时的值为["ROLE_XTGLY", "ROLE_YWGLY", "ROLE_YYGLY", "ROLE_ZH", "ROLE_ZHGLY"]，检查的值为["ROLE_YYGLY","ROLE_ZH","ROLE_XTGLY","ROLE_ZHGLY","ROLE_YWGLY"]
    assert update_user_param["roles"].sort() == test_get_user_roles_id(ip, port, headers).sort()


# 删除用户
def test_delete_user(ip, port, headers):
    ip_address = 'http://%s:%s' % (ip, port)
    # 删除编辑后的用户胡
    delete_user_id = test_get_user_account_list(ip, port, headers)[2][0]
    delete_user_response = requests.delete(
        url=ip_address + update_user_url + delete_user_id,
        headers=headers
    ).json()
    assert delete_user_response["status"] == 200
    # 断言用户名不在列表里
    assert create_user_param[0][0] not in test_get_user_account_list(ip, port, headers)[0]


# 编辑组织
@pytest.mark.parametrize('update_orgnization_param', update_orgnization_param)
def test_update_orgnization(ip, port, headers, update_orgnization_param):
    ip_address = 'http://%s:%s' % (ip, port)
    orgnization_id = test_get_create_orgnization_id(ip, port, headers)
    data = json.dumps(update_orgnization_param)  # 字典转化为字符串
    update_orgnization_response = requests.post(
        url=ip_address + update_orgnization_url + orgnization_id[0],
        headers=headers,
        data=data
    ).json()
    assert update_orgnization_response['status'] == 200
    assert update_orgnization_param["name"] in test_get_orgnization_name_list(ip, port, headers)


# 删除组织
def test_delete_orgnization(ip, port, headers):
    ip_address = 'http://%s:%s' % (ip, port)
    # 删除编辑后的组织
    delete_orgnization_id = test_get_update_orgnization_id(ip, port, headers)
    delete_orgnization_org2_id = test_get_create_orgnization_org2_id(ip, port, headers)
    print(test_get_orgnization_name_list(ip, port, headers))
    delete_orgnization_response = requests.delete(
        url=ip_address + update_orgnization_url + delete_orgnization_id[0],
        headers=headers
    ).json()
    delete_orgnization_org2_response = requests.delete(
        url=ip_address + update_orgnization_url + delete_orgnization_org2_id[0],
        headers=headers
    ).json()
    assert delete_orgnization_response["status"] == 200
    assert delete_orgnization_org2_response["status"] == 200
    # 断言组织已删除
    assert update_orgnization_param[0]["name"] not in test_get_orgnization_name_list(ip, port, headers)
    assert delete_orgnization_param[1]["name"] not in test_get_orgnization_name_list(ip, port, headers)
