import random
import re
from info.libs.yuntongxun import sms
from info.models import House, User
from . import api
from flask import request, jsonify, current_app, make_response, session, g
from info import redis_store, constants, db
from info.utils.captcha.captcha import  captcha
from info.utils.response_code import RET





#获取短信验证码
@api.route('/imagecode')
def imagecode():
    """
    1.获取参数,uuid
    :return:
    """
    image_code_id = request.args.get('cur')
    if not image_code_id :
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    name,text,image = captcha.generate_captcha()
    try:
        redis_store.setex('ImageCode_'+image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as f:
        current_app.logger.error(f)
        return jsonify(errno = RET.DATAERR, errmsg = '保存数据失败')
    else:
        response = make_response(image)
        response.headers['Content-Type'] = 'image/jpg'
        return response

#获取短信验证码
@api.route('/smscode',methods=['POST'])
def send_sms_code():

    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')

    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    try:
        real_image_code = redis_store.get('ImageCode_'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取数据失败')
    if not real_image_code :
        return jsonify(errno=RET.NODATA,errmsg='数据已失效')
    try:
        redis_store.delete('Image_Code_'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    if real_image_code.lower() != image_code.lower() :
        return jsonify(error=RET.DATAERR,errmsg='图片验证码错误')
    try :
        user = User.query.filter_by(mobile = mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')
    else :
        if user:
            return jsonify(errno=RET.DATAERR,errmsg='手机号已注册')

    sms_code ='%06d' %random.randint(0,999999)
    try:
        redis_store.setex('SMSCode_'+mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    try:
        ccp = sms.CCP()
        result = ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='发送短信异常')
    if result == 0:
        return jsonify(errno=RET.OK,errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR,errmsg='发送失败')

#注册
@api.route('/user',methods=['POST'])
def registers():
    mobile = request.json.get('mobile')
    sms_code = request.json.get('phonecode')
    password = request.json.get('password')
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    try:
        real_sms_code = redis_store.get('SMSCode_'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg='获取数据错误')
    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg='短信验证码过期')
    if real_sms_code != str(sms_code):
        return jsonify(errno=RET.DATAERR,errmsg='短信验证码错误')
    try :
        redis_store.delete('SMSCode_'+mobile)
    except Exception as e:
        current_app.logger.error(e)

    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询用户数据失败')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAERR,errmsg='手机号已注册')
    user=User()
    user.mobile = mobile
    user.name = mobile
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    session['user_id']=user.id
    session['user_mobile'] = mobile
    session['name'] = mobile
    return  jsonify(errno=RET.OK,errmsg='OK')


#登录
@api.route('/session',methods=['GET','POST'])
def logins():

    if request.method == 'GET':
        name = session.get('name')
        user_id = session.get('user_id')
        if not name :
            return jsonify(errno=RET.SERVERERR,errmsg='数据错误')
        else:
            return jsonify(errno=RET.OK,errmsg='OK',data={'name':name,'user_id':user_id})

    mobile = request.json.get('mobile')
    password = request.json.get('password')

    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询失败')
    if not user or not user.check_password(password):
        return jsonify(error=RET.PARAMERR,errmsg='用户名或密码错误')


    session['user_id'] = user.id
    session['user_mobile'] = user.mobile
    session['name'] = user.name

    return jsonify(errno=RET.OK,errmsg='OK')