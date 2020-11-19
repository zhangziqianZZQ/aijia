from flask import  current_app,request,jsonify,session# 全局对象表示当前应用
from  . import  api
from aijia.models import User,db
from aijia.utils.commons import RET
import re
from aijia import redis_storage
from aijia import constants

# 地址: api/v1.0/login
@api.route('/register',methods=['POST'])
def register():
    mobile = request.form.get('mobile')
    # phonecode = request.form.get("phonecode")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    print(mobile)
    # print(phonecode)
    print(password)
    print(password2)

    if not all([mobile, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    # try:
    #     real_sms_code = redis_storage.get("sms_code_%s" % mobile)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")

    # if real_sms_code is None:
    #     return jsonify(errno=RET.NODATA, errmsg="短信验证码失效")
    #
    # try:
    #     redis_storage.delete("sms_code_%s" % mobile)
    # except Exception as e:
    #     current_app.logger.error(e)

    # if real_sms_code != phonecode:
    #     return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")
    user = User(name=mobile, mobile=mobile)

    user.password = password  # 设置属性

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")

    # 保存登录状态到session中
    session["name"] = mobile
    session["mobile"] = mobile
    session["user_id"] = user.id

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="注册成功")

@api.route('/login',methods=['POST'])
def login():
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    if not re.match(r'1[356789]\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    user_ip = request.remote_addr
    try:
        access_nums = redis_storage.get('access_num_%s'%user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR,errmsg='错误次数过多')
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取用户信息失败')
    if user is None or not user.check_passwd(password):
        try:
            redis_storage.incr('access_num_%s'%user_ip)
            redis_storage.expire('access_num_%s'%user_ip,constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="用户名或密码错误")
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id
    return jsonify(errno=RET.OK,errmsg='登录成功')
