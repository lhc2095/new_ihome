from . import api
from flask import  request,jsonify,current_app,session,g
from info.models import House,Area
from info.utils.response_code import RET
from info import db
from info.utils.commons import required_login

@api.route('/user/houses')
@required_login
def new_house():

   user=g.user
   try:
       house_data=House.query.filter().all()
   except Exception as e:
       current_app.logger.error(e)
       return jsonify(errrno=RET.DBERR,errmsg='数据库查询失败')
   if not house_data:
       return jsonify(errno=RET.NODATA, errmsg='没有数据')
   houses=[]
   for house in house_data:
       houses.append(house.to_basic_dict())
   data={
        'houses':houses
    }

   return jsonify(errno=RET.OK,errmsg='OK',data=data)

@api.route('/areas')
def areas():
    try:
        areas_data=Area.query.filter().all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errrno=RET.DBERR, errmsg='数据库查询失败')
    if not areas_data:
        return jsonify(errno=RET.NODATA,errmsg='没有数据')
    areas = []
    for area in areas_data:
        areas.append(area.to_dict())

    return jsonify(errno=RET.OK, errmsg='OK', data=areas)

@api.route('/houses',methods=['GET','POST'])
@required_login
def new_houses():
        title=request.json.get('title')
        price=request.json.get('price')
        area_id=request.json.get('area_id')
        address=request.json.get('address')
        room_count=request.json.get('room_count')
        acreage=request.json.get('acreage')
        unit=request.json.get('unit')
        capacity=request.json.get('capacity')
        beds=request.json.get('beds')
        deposit=request.json.get('deposit')
        min_days=request.json.get('min_days')
        max_days=request.json.get('max_days')
        facility=request.json.get('facility')



        if not all([title,price,area_id,address,room_count,acreage,unit,capacity,beds,deposit,min_days,max_days,facility]):
            return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')

        try:
            area_id,room_count,acreage,capacity,min_days,max_days=int(area_id),int(room_count),int(acreage),int(capacity),int(min_days),int(max_days),
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errrno=RET.PARAMERR, errmsg='数据类型错误')

        house=House()
        house.title=title
        house.price=price
        house.area_id=area_id
        house.address=address
        house.room_count=room_count
        house.acreage=acreage
        house.unit=unit
        house.capacity=capacity
        house.beds=beds
        house.deposit=deposit
        house.min_days=min_days
        house.max_days=max_days
        house.user_id=7
        # house.facilities=facility
        try:
            db.session.add(house)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
        try:
            my_house=House.query.filter(House.title == title,House.address ==address).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库查询失败')

        if not my_house:
            return jsonify(errno=RET.NODATA, errmsg='没有数据')


        return jsonify(errno=RET.OK,errmsg='OK',house_id=house.to_full_dict())


