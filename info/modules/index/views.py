from flask import make_response, current_app

from . import index_blue



#进入首页
@index_blue.route('/<rege(r".*"):temp_index>')
def index(temp_index):
    if not temp_index:
        temp_index = 'index.html'
    if temp_index != 'favicon.ico':
        temp_index = 'html/'+temp_index

    response = make_response(current_app.send_static_file(temp_index))
    return response
