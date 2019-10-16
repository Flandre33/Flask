#encoding:utf-8
from flask import Blueprint,render_template,request,flash,redirect,url_for,session
from .forms import  RegisterForm,LoginForm,CommentForm
from .models import Members
from exts import db
from config import MEMBER_USER_ID
from .recursion import build_cat_tree,build_cat_table
import time, datetime, os
from datetime import timedelta
#要导入上级目录中的模块，可以使用sys.path
import sys
# 导入上级目录
sys.path.append('../')
# 导入上级目录中的内容
from ..admin.models import Articles,Articles_Cat,Users,Comment
from flask_sqlalchemy import get_debug_queries
from logging.handlers import RotatingFileHandler
import logging


# 首页
bp=Blueprint("front",__name__)#前台访问不需要前缀
@bp.route('/')
def index():
    return  "这是前台首页！"

# 注册
@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('front/register.html')
    if request.method == 'POST':
        form = RegisterForm(request.form)
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        email = form.email.data
        if password1 != password2:
            # 用消息闪现予以提示
            flash('两次输入的密码不一样', 'error')
        else:
            user = Members(username=username, password=password1, email=email)
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录','ok')
        return redirect(url_for('front.register'))

# 登录
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        url = request.args.get('url')
        if url == '/log_out':
            url = '/'
        if url == None:
            session['url'] = None
        else:
            session['url'] = url 
        return render_template('front/login.html')
    else:
        form = LoginForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            users = Members.query.filter_by(username=username).first()
            # 如果用户存在
            if users: 
                # 验证用户名和密码
                if username == users.username and users.check_password(password):
                    # 将username对应信息存到session中
                    session[MEMBER_USER_ID] = users.username 
                    # 实现会话持久化
                    session.permanent = True
                    bp.permanent_session_lifetime = timedelta(days=1)
                else:
                    flash('账号或密码错误','error')
                    return redirect(url_for('front.login'))
            # 用户输入错误的用户名
            else:
                flash('用户账号错误', 'error')
                return redirect(url_for('front.login'))
        # 表单验证失败
        else:
            # 获取表单验证出错信息
            errors = form.errors
            flash(errors, 'error')
            # 登录失败，网页重定向岛用户登陆页
            return redirect(url_for('front.login'))
        # 取得用户名
        username = session.get(MEMBER_USER_ID)
        session['username'] = username
        if session['url'] == None:
            return render_template('front/index.html', username=username)
        else:
            # 网页重定向到用户登录之前的页面
            return redirect(session['url'])

# 注销
@bp.route('/log_out')
def log_out():
    # 清除session
    session.pop(MEMBER_USER_ID, None)
    session.pop('username', None)
    return redirect(url_for('front.index'))

# 文章详情页面路由
@bp.route('/article_details/<int:id>', methods=['GET', 'POST'])
def article_details(id):
    if request.method == 'GET':
        # 取得新闻详情
        test_article = Articles(
            aid = 1,
            title = '这是文章标题',
            source = '这是文章来源',
            keywords = '这是关键词',
            description = '这是文章摘要',
            body = '这是文章内容'
            )
        #db.session.add(test_article)
        #db.session.commit()
        news1 = Articles.query.filter(Articles.aid==id).first_or_404()
        author1 = Users.query.filter(Users.uid==news1.author_id).first()
        if author1:
            author = author1.username
        else:
            author = '匿名'
        # 更新单击次数
        db.session.query(Articles).filter_by(aid=id).update({
            Articles.clicks:Articles.clicks+1
            })
        db.session.commit()
        news2 = Articles.query.filter(Articles.aid<id).order_by(Articles.aid.desc()).first()
        news3 = Articles.query.filter(Articles.aid>id).order_by(Articles.aid.asc()).first()
        # 热门资讯
        news4 = Articles.query.filter(Articles.is_delete==0).order_by(Articles.clicks.desc()).limit(5)
        list = []
        data = {}
        nav = Articles_Cat.query.all()
        for cat in nav:
            data = dict(cat_id=cat.cat_id, parent_id=cat.parent_id, cat_name=cat.cat_name)
            list.append(data)
        # 构建目录树
        cat = build_cat_tree(list, 0, 0)
        # 构建含有CSS样式的下拉列表菜单
        zz = build_cat_table(cat, parent_title='顶级菜单')
        return render_template('front/article_details.html', news1=news1,news2=news2,news3=news3,news4=news4,author=author,cat=zz)
    else:
        if request.method=='POST':#如果访问方法为POST方法
            form = CommentForm(request.form)  # 实例化定义的添加评论表单;
            data = form.data#获取表单数据
            id = data['article_id']#从表单中取得article_id的值
            if session.get('username') == None:#用户没有登录，则跳转到登陆页面
                url=url_for('front.login') +'?url=article_details/'+id#构造重定向网址
                return redirect(url)#网页重定向
            if form.validate():#如果表单验证通过
                comment_content = data['comment_content']#从表单中取值赋给comment_content
                captcha = data['captcha']#从表单中取值赋给captcha
                id = data['article_id']#从表单中取值赋给id
                title = data['article_title']#从表单中取值赋给title
                if session.get('image').lower() != captcha.lower():#如果POST过来的验证码与sessin中的验证码不相等
                    flash('验证码不对', 'error')  # 如果表单验证没有通过，则用消息闪现机制予以提示

                else:  #准备提交表单信息
                    username=session.get('username')#从session中取得username
                    user=Members.query.filter(Members.username==username).first_or_404()#根据用户名取得用户ID
                    uid=user.uid

                    #准备POST的数据
                    post = Comment(
                        title=title,  # 评论的文章标题
                        aid=id,  # 评论的文章ID
                        comment=comment_content,  # 评论内容
                        status=0, # 评论审核转台
                        parent_id=1,  # 评论的层次关系
                        add_time=datetime.datetime.now(),
                        user_name=session.get('username'),  # 获取session
                        user_id=uid,#评论用户ID
                        comment_ip=request.remote_addr  # 评论者的IP地址
                    )
                    db.session.add(post)  # 添加评论
                    db.session.commit()  # 提交事务
                    flash('评论添加成功', 'ok')  # 消息闪现
                    return redirect(url_for('front.article_details',id=id))#网页重定位
            else:
                errors = form.errors  # 获取表单验证出错信息
                flash(errors, 'error') # 如果表单验证没有通过，则用消息闪现机制予以提示
                return redirect(url_for('front.article_details',id=id)) # 登录失败，网页重新定位到用户登陆页

# 404等错误处理
@bp.app_errorhandler(404)
def error_404(error):
    return render_template('front/404.html'), 404

# 500等错误处理
@bp.app_errorhandler(500)
def error_500(error):
    return render_template('front/404.html'), 404

# 记录慢记录
@bp.after_request
def after_request(response):
    formatter = logging.Formatter(  # 设定日志格式
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('slow_query.log', maxBytes=10000, backupCount=10)
    handler.setLevel(logging.WARN)
    handler.setFormatter(formatter)
    logger = logging.getLogger("logger")
    logger.addHandler(handler)
    for query in get_debug_queries():
        if query.duration >= 0:
            logger.warn(
                ('\nContext:{}\nSLOW QUERY: {}\nParameters: {}\nSTART_TIME: {}\nDuration: {}\n').format(query.context,
                                                                                                        query.statement,
                                                                                                        query.parameters,
                                                                                                        query.start_time,
                                                                                                        query.duration))