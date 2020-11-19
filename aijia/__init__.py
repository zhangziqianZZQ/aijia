import redis
from flask_session import Session
from flask import Flask
from config import config_map  #通过字典调用不同配置类
from flask_sqlalchemy import SQLAlchemy #数据库模块
from flask_wtf import CSRFProtect  # 表单安全
from aijia.utils.commons import  MyRegexConverter #导入自己写的完整的正则转换器（验证路由规则）

db = SQLAlchemy()  #创建数据库对象
redis_storage = None  #创建缓存数据库redis连接对象

#####  日志配置开始
import logging  # 导入python标准库自带的日志模块
from logging.handlers import RotatingFileHandler  # 日志信息转换文件存储
logging.basicConfig(level=logging.WARNING)  # 设置日志只记录警告级别的信息
# 第一次将日志保存到logs/log文件中，当文件大小超过100M后会将文件改名为log1,同时生成一个新文件log,
# 如果文件大小超过再次超过100M后，会将文件改名为log2,同时生成一个空的日志文件log,依次类推....
# 创建日志记录器，指明日志的保存路径，每个日志文件的最大大小，保存的日志文件个数的上限
# 日志文件路径logs/log中！ 暂时无法识别相对路径！
file_log_handler = RotatingFileHandler("logs/log",maxBytes=1024*1024*100,backupCount=10)
# 创建日志文件的格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
#为刚创建的日志文件创建日志记录器
file_log_handler.setFormatter(formatter)
#为全局的日志工具对象(flask app 使用的)添加日志记录器
logging.getLogger().addHandler(file_log_handler)
#####  日志配置结束

# 工厂模块初始化app(传递不同参数，生成不同的类，该思想雷同于生活中的工厂，学名“工厂模式”)
def create_app(config_name):
    app = Flask(__name__)
    # 根据配置产生名字获取配置类
    config_class = config_map.get(config_name) # develop   product
    app.config.from_object(config_class)

    # 初始化数据库,数据库初始化参数从app中读取
    db.init_app(app)
    # 初始化redis
    import redis
    from flask_session import Session
    global redis_storage  # redis对象变为全局的【global：全局，表示该变量再当前项目中都能访问到】
    redis_storage = redis.StrictRedis(host=config_class.REDIS_HOST,port=config_class.REDIS_PORT)
    Session(app)  # 利用flask-session模块，将session数据存储到redis中

    # 为flask项目添加csrf防护
    # CSRFProtect(app)

    # url 路由可以扩展正则转换器！
    app.url_map.converters['re'] =MyRegexConverter

    # 注册项目模块(蓝图)
    from aijia import api_1_0
    app.register_blueprint(api_1_0.api,url_prefix='/api/v1.0') # url访问名 url_prefix
    # 注册提供静态资源的蓝图！
    from aijia import web_html
    app.register_blueprint(web_html.html)  # web_html文件名，html是蓝图名字
    # redis 数据库(缓存数据库)

    return app
