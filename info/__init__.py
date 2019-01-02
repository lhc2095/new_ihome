from flask import  Flask
from flask_session import  Session
from flask_sqlalchemy import  SQLAlchemy
from config import config_dict,Config
from logging.handlers import RotatingFileHandler
import logging

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


from redis import StrictRedis
#实例化redis对象，用来存储和业务相关的数据----图片验证码，短信验证码，昵称
redis_store =StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_POST,decode_responses=True)

#实例化sqlalchemy对象，对数据库进行操作
db=SQLAlchemy()

#开启csrf保护，使用wtf扩展包
from flask_wtf import CSRFProtect,csrf


def create_app(config_name):

    #实例化app
    app=Flask(__name__)
    #使用配置对象
    app.config.from_object(config_dict[config_name])
    #通过函数来让db和app进行关联
    db.init_app(app)
    #Session初始化
    Session(app)


    #开启csrf保护
    CSRFProtect(app)

    #生成csrf_token,并且把token写入客户端浏览器的cookie中
    #在每次请求后，生成csrf_token，并且把token写入客户端的浏览器的cookie中
    @app.after_request
    def after_request(response):
        #生成csrf_token
        csrf_token=csrf.generate_csrf()
        # 使用响应对象来设置csrf_token
        response.set_cookie('csrf_token', csrf_token)
        # 返回响应
        return response

    from info.modules.index.views import index_blue  # 导入主页蓝图
    from info.modules.api import api  # 导入注册登录蓝图

    app.register_blueprint(index_blue)  # 注册主页蓝图
    #添加自定义转换器
    from info.utils.commons import RegexConverter
    app.template_filter['rege'] = RegexConverter

    app.register_blueprint(api,url_prefix='/api/v1.0')  # 注册注册登录蓝图

    return app