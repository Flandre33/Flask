from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# 定义用户模型
class Members(db.Model):
	__tablename__ = 'member'
	uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(50), nullable=False, unique=True)
	_password = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(50), nullable=False, unique=True)
	vatar = db.Column(db.String(80), nullable=True) # 用户头像
	nickname = db.Column(db.String(50), nullable=True) # 用户昵称
	sex = db.Column(db.String(2), default=0) # 性别
	telephont = db.Column(db.String(11))
	status = db.Column(db.Integer) # 状态
	def __init__(self, username, password, email):
		'''初始化'''
		self.username = username
		self.password = password
		self.email = email

	@property
	def password(self):
		return self._password

	@password.setter
	def password(self, raw_password):
		self._password = generate_password_hash(raw_password)

	def check_password(self, raw_password):
		result = check_password_hash(self.password, raw_password)
		return result
	