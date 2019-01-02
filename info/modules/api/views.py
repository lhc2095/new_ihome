
from info.models import House
from info.utils.commons import required_login
from . import api
from flask import request, jsonify, current_app, make_response, session, g
from info import redis_store, constants
from info.utils.captcha.captcha import  captcha
from info.utils.response_code import RET


@api.route('/houses/index')
@required_login
def house():
    """
    1.获取参数,数据库图片
    2.返回数据
    :return:
    """
    try:
        houses = House.query.order_by(House.order_count.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库查询错误')
    if not houses :
        return jsonify(errno=RET.NODATA,errmsg='数据库没有数据')
    houses = []
    for i in houses:
        house.append(i.to_basic_dict())
    data = {
        'houses':houses
    }

    return jsonify(errno=RET.OK,errmsg='OK',data=data)















