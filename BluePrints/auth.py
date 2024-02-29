import flask
from flask import Blueprint, request, jsonify
from models import EmailVerifyCodeModel, UserModel, AccountFingerPrintModel, LoggerModel
from datetime import datetime
from Utils import Generator, Detector
from exts import db

authBp = Blueprint("auth", __name__, url_prefix="/auth")


# 注册验证邮箱
@authBp.route("/reg", methods=['POST'])
def register():
    email = request.values.get("email")
    pwd = request.values.get("pwd")
    nick = request.values.get("nick")
    code = request.values.get("code").upper()
    if not Detector.check_Nick_Available(nick):
        return Generator.gen_rest_rule(400, {}, "用户名重复")  # 用户名重复
    record = EmailVerifyCodeModel.query.get(email)
    if record is None or record.isused is True:
        return Generator.gen_rest_rule(400, {}, "邮箱无效")  # 无记录或已使用
    else:
        if datetime.now().__sub__(record.send_time).seconds > 1200:  # 验证码发送20分钟后失效
            return Generator.gen_rest_rule(400, {}, "验证超时")  # 验证码失效
        else:
            if code.__eq__(record.code):
                record.isused = True
                new_user = UserModel()
                new_user.email = email
                new_user.nick = nick
                new_user.password = Generator.gen_pwd_sha256(pwd)
                db.session.add(new_user)
                db.session.commit()
                user_fingerprint = AccountFingerPrintModel()
                user_fingerprint.id = new_user.id
                user_fingerprint.fingerprint = Generator.gen_fingerprint(new_user.id)
                db.session.add(user_fingerprint)
                db.session.commit()
                resp = flask.make_response(Generator.gen_rest_rule(200,
                                                                   {
                                                                       'nick': nick,
                                                                       'email': email,
                                                                       'id': new_user.id,
                                                                       'fp': user_fingerprint.fingerprint
                                                                   },
                                                                   "注册成功"), 200)
                loggerModel = LoggerModel()
                loggerModel.exec_id = new_user.id
                loggerModel.exec_type = 1
                loggerModel.info = f"注册IP:{request.remote_addr}"
                db.session.add(loggerModel)
                db.session.commit()
                return resp
            else:
                return Generator.gen_rest_rule(400, {}, "错误的验证码")  # 验证码错误


# 登录账号
@authBp.route("/log", methods=['POST'])
def login():
    login_pwd = Generator.gen_pwd_sha256(request.values.get("pwd"))
    login_email = request.values.get("email")
    user = UserModel.query.filter_by(email=login_email).first()
    if user is None:
        return Generator.gen_rest_rule(400, {}, "邮箱不存在")
    else:
        if user.password == login_pwd:
            user_fingerprint = AccountFingerPrintModel.query.get(user.id)
            user_fingerprint.id = user.id
            user_fingerprint.fingerprint = Generator.gen_fingerprint(user.id)
            db.session.add(user_fingerprint)
            db.session.commit()
            resp = flask.make_response(Generator.gen_rest_rule(200,
                                                               {
                                                                   'id': user.id,
                                                                   'nick': user.nick,
                                                                   'desc': user.desc,
                                                                   'email': user.email,
                                                                   'fp': user_fingerprint.fingerprint
                                                               },
                                                               "登录成功"), 200)
            loggerModel = LoggerModel()
            loggerModel.exec_id = user.id
            loggerModel.exec_type = 1
            loggerModel.info = f"登录IP:{request.remote_addr}"
            db.session.add(loggerModel)
            db.session.commit()
            return resp
        else:
            return Generator.gen_rest_rule(400, {}, "密码错误")
