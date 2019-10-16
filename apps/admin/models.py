#encoding:utf-8
from exts import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

class Users(db.Model):
    __tablename__='user'
    uid=db.Column(db.Integer,primary_key=True,autoincrement=True)
    #gid=db.Column(db.Integer,nullable=True)
    username=db.Column(db.String(50),nullable=False,unique=True)#用户名不能为空,而且必须是唯一的
    #password=db.Column(db.String(100),nullable=False)#密码不能为空
    _password = db.Column(db.String(100), nullable=False)  # 密码不能为空
    email=db.Column(db.String(50),nullable=False,unique=True)#用户邮箱不能为空，而且必须是唯一的
    # avatar=db.Column(db.String(80),nullable=True)#用户头像
    # nickname=db.Column(db.String(50),nullable=True)#用户昵称
    is_super = db.Column(db.SmallInteger) # 是否为超级管理员，0为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('role.id')) # 所属角色
    reg_time=db.Column(db.DateTime,default=datetime.now)
    articles = db.relationship("Articles", lazy="dynamic")  # 一个栏目对应多个文章
    def __init__(self,username,password,email):
         self.username=username
         self.password=password
         self.email=email
    # #获取密码
    @property
    def password(self):
         return self._password
    # 设置密码
    @password.setter
    def password(self,raw_password):
         self._password=generate_password_hash(raw_password)#密码加密
    # 检查密码
    def check_password(self,raw_password):
         result=check_password_hash(self.password,raw_password)#
         return result

#定义文章分类开始
class Articles_Cat(db.Model):
    __tablename__='article_category'
    cat_id=db.Column(db.Integer,primary_key=True,autoincrement=True)#分类ID
    parent_id=db.Column(db.Integer,nullable=False)#分类父ID,父ID不能为空
    cat_name=db.Column(db.String(20),nullable=False)#栏目名称
    keywords=db.Column(db.String(20),nullable=False)#栏目关键字
    description=db.Column(db.Text,nullable=True)#栏目描述可以为空
    cat_sort=db.Column(db.Integer,nullable=True)#栏目排序
    # template=db.Column(db.String(80),nullable=False)# 栏目模板
    status=db.Column(db.Integer,nullable=False)#显示还是隐藏
    dir=db.Column(db.String(80),nullable=False)#如果实现静态化，该栏目的保存路径
    articles = db.relationship("Articles", lazy="dynamic")#一个栏目对应多个文章

#建立文章和标签的关联表
article_tag = db.Table('article_tag',
                    db.Column('article.aid',db.Integer,db.ForeignKey('article.aid'),primary_key=True),
                    db.Column('tag.tid',db.Integer,db.ForeignKey('tag.tid'),primary_key=True))


# 文章
class Articles(db.Model):
    __tablename__ = 'article'
    aid = db.Column(db.Integer, primary_key=True, autoincrement=True) # 文章id
    cat_id = db.Column(db.Integer, db.ForeignKey("article_category.cat_id")) # 分类ID
    title = db.Column(db.String(255), nullable=False) # 文章标题
    shorttitle = db.Column(db.String(64), nullable=True) # 短标题
    source = db.Column(db.String(64), nullable=False) # 文章来源
    keywords = db.Column(db.String(64), nullable=False) # 关键词
    description = db.Column(db.String(512), nullable=False) # 文章摘要
    body = db.Column(db.Text, nullable=False) # 文章内容
    clicks = db.Column(db.Integer, default=0) # 点击量
    picture = db.Column(db.String(255)) # 图片路径
    author_id = db.Column(db.Integer, db.ForeignKey('user.uid')) # 文章作者id
    allowcomments = db.Column(db.Integer, default=0) # 是否允许评论
    status = db.Column(db.Integer, default=0) # 当前文章状态，1审核中，0通过，-1不通过
    create_time = db.Column(db.DateTime, default=datetime.now) # 文章添加时间
    is_delete = db.Column(db.Boolean, default=0) # 删除标志
    tags = db.relationship('Articles_Tag', secondary=article_tag, backref=db.backref('articles'))

# 文章标签
class Articles_Tag(db.Model):
     __tablename__ = 'tag'
     tid = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 分类ID
     aid = db.Column(db.Integer)  # 外键,文章ID
     cat_id=db.Column(db.SmallInteger)#属于哪个文章栏目下的tag
     tag = db.Column(db.String(40), nullable=False)  # 文章标签,nullable=false是这个字段在保存时必需有值

#评论
class Comment(db.Model):
    __tablename__='comment'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    aid=db.Column(db.Integer)#外键，文章ID
    title=db.Column(db.String(255))#评论的文章标题
    user_id=db.Column(db.Integer)#用户ID
    user_name=db.Column(db.String(200))#用户名
    comment=db.Column(db.Text)#评论内容
    status = db.Column(db.Integer, default=0)  # 当前评论状态 如果为0代表审核通过，1代表审核中，-1代表审核不通过
    parent_id=db.Column(db.Integer)#评论的父ID
    comment_ip=db.Column(db.String(255))#评论者的IP地址
    add_time=db.Column(db.DateTime,default=datetime.now)#评论添加时间

# 管理员登陆日志
class Admin_Log(db.Model):
    __tablename__ = 'adminlog'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.ForeignKey('user.uid')) # 定义外键
    operate = db.Column(db.String(300)) # 操作行为
    ip = db.Column(db.String(100)) # ip
    # time = db.Column(db.String(100)) # 时间戳
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

# 定义权限数据模型
class Auth(db.Model):
    __tablename__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(255), unique=True) # 权限地址
    parent_id=db.Column(db.Integer,default=0)#父ID,不能为空
    status=db.Column(db.Integer, default=0)#0允许显示，-1表示不显示
    add_time = db.Column(db.DateTime, index=True, default=datetime.utcnow) # 添加时间

# 定义角色数据模型
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description=db.Column(db.String(600))#角色描述
    auths = db.Column(db.String(600)) # 权限列表
    add_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    admins = db.relationship('Users', backref='role')
