import unittest
import sys
sys.path.append('../../') # 设定app.py所在路径，根目录
from app import create_app

app = create_app()
class TestIndex(unittest.TestCase):
	def print_info(self, a):
		print('clearing...')

	def setUp(self):
		self.app = app.test_client() # Flask客户端可以模拟发送请求
		print('set up')

	def tearDown(self):
		print('down')
		self.addCleanup(self.print_info, 'clearing...')

	def test_index(self):
		pass


