from flask import make_response, current_app

from . import index_blue



#进入首页
@index_blue.route('/')
def index():
    response = make_response(current_app.send_static_file('html/index.html'))
    return response
