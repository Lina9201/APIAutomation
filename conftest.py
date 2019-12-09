import pytest
import requests

authentication_url_path = "/v1/tokens"

json_login = {
    "authType": "password",
    "params": {
        "username": "zhon",
        "password": "jixlb2tIrjF5t/bYQTXz4Q=="
    }
}


def pytest_addoption(parser):
    parser.addoption("--ip", action="store", default="172.23.1.2", help="please input target VM ip.")
    parser.addoption("--port", action="store", default="api", help="please input target service port.")


@pytest.fixture(scope="session")
def ip(request):
    return request.config.getoption("--ip")


@pytest.fixture(scope="session")
def port(request):
    return request.config.getoption("--port")


@pytest.fixture(scope="session")
def uri(ip,port):
    uri = "http://%s/%s" % (ip, port)
    return uri


@pytest.fixture(scope="session")
def auth_token(uri):
    headers = {"User-Agent": "automation",
               "content-type": "application/json;charset=UTF-8"
               }

    post_response = requests.post(url=uri + authentication_url_path,
                                  json=json_login,
                                  headers=headers)

    assert post_response.status_code == requests.status_codes.codes.OK
    resp_payload = post_response.json()
    assert resp_payload['status'] == 200  # to be defined.
    auth_token = resp_payload['data']['key']

    return auth_token


@pytest.fixture(scope="session")
def headers(uri):
    headers = {"User-Agent": "automation",
               "content-type": "application/json;charset=UTF-8"
               }

    post_response = requests.post(url=uri + authentication_url_path,
                                  json=json_login,
                                  headers=headers)

    assert post_response.status_code == requests.status_codes.codes.OK
    resp_payload = post_response.json()
    assert resp_payload['status'] == 200  # to be defined.
    auth_token = resp_payload['data']['key']

    headers = {"User-Agent": "automation",
               "content-type": "application/json;charset=UTF-8",
               "T-AUTH-TOKEN": auth_token}
    return headers


