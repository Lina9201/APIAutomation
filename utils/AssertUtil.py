# -*- coding: utf-8 -*-
# @Time    : 2019/10/14 10:47
# @Author  : zhuxuefei

import json

class AssertUtil:
    def assert_code(self, code, expected_code):
        """
        验证返回code一致
        :param code:
        :param expected_code:
        :return:
        """
        try:
            assert int(code) == int(expected_code)
        except:
            print("code error")
            raise

    def assert_body(self, body, expected_body):
        """
        验证返回结果内容相等
        :param body:
        :param expected_body:
        :return:
        """
        try:
            assert body == expected_body
        except:
            print("body error")
            raise


    def assert_in_body(self, body, excepted_body):
        """
        验证返回结果是否包含预期的结果
        :param body:
        :param excepted_body:
        :return:
        """
        try:
            body = json.dumps(body)
            assert excepted_body in body
        except:
            print("body in error")
            raise