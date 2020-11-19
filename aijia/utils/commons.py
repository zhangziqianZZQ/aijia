from werkzeug.routing import BaseConverter

class MyRegexConverter(BaseConverter):
    def __init__(self,url_map,regex):
        super(MyRegexConverter,self).__init__(url_map)
        self.regex = regex

import functools
from flask import session,jsonify,g
from aijia.utils.response_code import RET
def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is not None:
            g.user_id = user_id
            return view_func(*args,**kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR,errmsg='未登录')
    return wrapper