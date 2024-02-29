import hashlib
import logging
import random
import datetime
from flask import jsonify
from flask_mail import Message
from exts import mail


def gen_email_code(email):
    random.seed(f"{email}{datetime.datetime.now()}")
    return ''.join(random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890", k=6))


def gen_pwd_sha256(pwd):
    hash_obj = hashlib.sha256()
    hash_obj.update(pwd.encode('utf-8'))
    return hash_obj.hexdigest()


def gen_email(email, content, subject):
    msg = Message(recipients=[email], subject=subject, body=content)
    try:
        mail.send(msg)  # 发送邮件
        return True
    except Exception as e:
        logging.getLogger().error(Exception.args)
        return False


def gen_rest_rule(code, data, message):
    content = {
        'code': code,
        'data': data,
        'message': message
    }
    return jsonify(content)


def gen_fingerprint(user_id):
    hash_obj = hashlib.sha256()
    hash_obj.update(datetime.datetime.now().timestamp().__str__().encode('utf-8'))
    hash_obj.update(f"{user_id}".encode('utf-8'))
    return hash_obj.hexdigest()
