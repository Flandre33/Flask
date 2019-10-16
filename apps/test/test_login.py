import unittest
import json
import sys
sys.path.append('../../')
from app import create_app
from flask import json

app = create_app()
class TestLogin(unittest.TestCase):
	def print_info(self, a):
		print('clearing...')

	def setUp(self):
		app.testing = True
		self.client = app.test_client()
		print('测试用户登录开始，使用错误的用户名或密码')

	def tearDown(self):
		print('测试用户登录结束，可以清除相应的测试数据')
		self.addCleanup(self.print_info, 'clearing...')

	def test_error_username_password(self):
		# 测试错误的用户名或密码，服务器发出的JSON格式数据放入response
		response = app.test_client().post('/login?url=/', data={"username":"zhangsan", "password":"1111"})
		# 使用response.data取得服务器相应数据
		resp_json = response.data 
		# 以json格式解析数据
		resp_dict = json.loads(resp_json)
		# 使用断言，验证resp_dict是否包含code子串，若code不是resp_dict的子串，返回False
		self.assertIn('code', resp_dict)
		# 使用get方法获取resp_dict中的code
		code = resp_dict.get('code')
		# 使用断言，验证code的值是否为2，不为2返回False，否则OK
		self.assertEqual(code, 2)