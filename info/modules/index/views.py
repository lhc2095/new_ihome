from flask import make_response, current_app
from flask import Blueprint

index_blue=Blueprint('index_blue',__name__)



# 进入首页
@index_blue.route('/<re(r".*"):temp_index>')
def index(temp_index):

    response = make_response(current_app.send_static_file('html/index.html'))

    return response
