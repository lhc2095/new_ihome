

#自定义转换器
import functools

from flask import session, current_app, g
from werkzeug.routing import BaseConverter

from info.models import User


class RegeConverter(BaseConverter):
    def __init__(self,url_map,*args):
        super(RegeConverter,self).__init__(url_map)
        self.regex = args[0]


#登录验证装饰器
def required_login(f):
    functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.filter_by(id=user_id).first()
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args,*kwargs)
    return wrapper
