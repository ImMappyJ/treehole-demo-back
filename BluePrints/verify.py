from flask import Blueprint, request, jsonify
from models import EmailVerifyCodeModel, UserModel
from datetime import datetime
from Utils import Generator
from exts import db

verifyBp = Blueprint("verifyBp", __name__, url_prefix="/verify")


# 注册创建邮箱验证码
@verifyBp.route("/email", methods=['GET'])
def verify_email_create():
    email = request.args["email"]
    record = EmailVerifyCodeModel.query.get(email)
    if record is None:
        model = EmailVerifyCodeModel()
        model.email = email
        model.code = Generator.gen_email_code(email)
        db.session.add(model)
        db.session.commit()
        Generator.gen_email(email=email, content="您的邮箱验证码为"+model.code, subject="TreeHole邮箱验证码")
        return Generator.gen_rest_rule(200,
                                       {
                                           'email': email,
                                       },
                                       "获取成功")
    else:
        if datetime.now().__sub__(record.send_time).seconds > 60 and record.isused is False:  # 需要等待5分钟才可以进行下一次请求验证码
            db.session.delete(record)
            db.session.commit()
            model = EmailVerifyCodeModel()
            model.email = email
            model.code = Generator.gen_email_code(email)
            db.session.add(model)
            db.session.commit()
            Generator.gen_email(email=email, content="您的邮箱验证码为" + model.code, subject="TreeHole邮箱验证码")
            return Generator.gen_rest_rule(200,
                                           {
                                               'email': email,
                                           },
                                           "获取成功")
        else:
            return Generator.gen_rest_rule(400,
                                           {},
                                           "操作频繁")
