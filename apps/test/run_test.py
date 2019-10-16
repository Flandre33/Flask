import unittest
import os

class RunCase(unittest.TestCase):
	def test_case(self):
		case_path = os.getcwd()
		# discover()方法会根据测试目录所有与test_*.py名称模式匹配的测试文件，并加载其内容
		discover = unittest.defaultTestLoader.discover(case_path, pattern='test_*.py')
		# TextTestRunner类将用例执行的结果以text形式输出，分为0-6级，0最简单，2为完整信息
		runner = unittest.TextTestRunner(verbosity=2)
		runner.run(discover)

if __name__ == '__main__':
	unittest.main()


