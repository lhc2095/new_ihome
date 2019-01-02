from . import  passport_blue
from flask import  request,jsonify,current_app,make_response
from info import redis_store,constants
from info.utils.captcha.captcha import  captcha
from info.utils.response_code import RET


# 进入注册页面
@passport_blue.route('/register')
def register():
    from manage import app
    return app.send_static_file('register.html')


#生成验证码
@passport_blue.route('/api/v1.0/imagecode')
def image_code():
    image_code_id=request.args.get('cur')
    if not image_code_id:
        return jsonify(errno=RET.NODATA,errmsg='参数缺失')
    name,text,image=captcha.generate_captcha()
    try:
        redis_store.setex('ImageCode_'+image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    response=make_response(image)
    response.headers['Content-Type']='image/jpg'
    return response


