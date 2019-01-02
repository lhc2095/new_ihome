from flask_script import Manager      #导入管理器
from flask_migrate import  Migrate,MigrateCommand  #导入迁移框架
from info import create_app,db,models
# from info.models import User    # 使用命令行创建管理员用户用


app=create_app('development')

Migrate(app,db)
manage=Manager(app)
manage.add_command('db',MigrateCommand)

#创建管理员用户------------------------------------
# @manage.option('-n', '-name', dest='name')
# @manage.option('-p', '-password', dest='password')
# def create_supperuser(name, password):
#     if not all([name, password]):
#         print('参数缺失')
#     user = User()
#     user.nick_name = name
#     user.mobile = name
#     user.password = password
#     user.is_admin = True
#     try:
#         db.session.add(user)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         print(e)
#     print('管理员创建成功')
# -----------------------------------------------

if __name__ == '__main__':
    print(app.url_map)
    manage.run()
