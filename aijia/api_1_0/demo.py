from flask import  current_app  # 全局对象表示当前应用
from  . import  api

@api.route('/index')
def index():
    current_app.logger.error('测试：Error信息...,都会被写到log文件中')
    current_app.logger.warn('测试:worn信息...')
    current_app.logger.debug('测试:debug信息...')
    current_app.logger.info('测试:info信息普通信息,...')


    # ORM操作数据库！
    return "测试方法。演示日志使用！"
