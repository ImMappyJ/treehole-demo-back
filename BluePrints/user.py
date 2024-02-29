from flask import Blueprint, request

from Utils import Generator, Detector
from models import AccountFingerPrintModel, UserModel, ArticleModel, CommentModel, LikeRecordModel, LoggerModel
from exts import db

userBp = Blueprint("userBp", __name__, url_prefix="/user")


@userBp.route("/get", methods=['POST'])
def getInfo():
    fp = request.values.get("fp")
    relation = AccountFingerPrintModel.query.filter_by(fingerprint=fp).first()
    if relation is None:
        return Generator.gen_rest_rule(400, {}, "用户不存在")
    user = relation.account
    return Generator.gen_rest_rule(200, {
        'id': user.id,
        'nick': user.nick,
        'desc': user.desc,
        'email': user.email,
        'group': user.group
    }, "获取成功")


@userBp.route("/get/articles", methods=['GET'])
def article_get_byauthor():
    author_id = request.args.get("id")
    author = UserModel.query.get(author_id)
    if author is None:
        return Generator.gen_rest_rule(400, {}, "该用户不存在")
    result = author.articles
    articles = []
    for article in result:
        comment_number = len(article.comments)
        article_dict = {
            "id": article.id,
            "post_time": article.post_time,
            "type": article.type.type,
            "title": article.title,
            "context": article.context,
            "view": article.view,
            "like": article.like,
            "comment": comment_number
        }
        articles.append(article_dict)

    return Generator.gen_rest_rule(200, {
        'articles': articles,

    }, "获取成功")


@userBp.route("/get/articles", methods=['POST'])
def article_get_byfp():
    fp = request.values.get("fp")
    relation = AccountFingerPrintModel.query.filter_by(fingerprint=fp).first()
    if relation is None:
        return Generator.gen_rest_rule(400, {}, "用户不存在")
    user = relation.account
    result = user.articles
    articles = []
    for article in result:
        comment_number = len(article.comments)
        article_dict = {
            "id": article.id,
            "post_time": article.post_time,
            "type": article.type.type,
            "title": article.title,
            "context": article.context,
            "view": article.view,
            "like": article.like,
            "comment": comment_number
        }
        articles.append(article_dict)

    return Generator.gen_rest_rule(200, {
        'articles': articles,

    }, "获取成功")


@userBp.route("/get/comments", methods=['GET'])
def comment_get_byauthor():
    author_id = request.args.get("id")
    author = UserModel.query.get(author_id)
    if author is None:
        return Generator.gen_rest_rule(400, {}, "该用户不存在")
    comments = CommentModel.query.filter_by(author_id=author_id).all()
    comment_list = []
    for comment in comments:
        comment_dict = {
            "comment_id": comment.comment_id,
            "post_time": comment.post_time,
            "article_id": comment.article_id,
            "comment": comment.comment,
            "father_comment_id": comment.father_comment_id
        }
        comment_list.append(comment_dict)
    return Generator.gen_rest_rule(200, {"comments": comment_list}, "获取成功")


@userBp.route("/change/nick", methods=['POST'])
def nick_change():
    user_id = request.values.get("id")
    new_nick = request.values.get("new_nick")
    fp = request.values.get("fp")
    relation = AccountFingerPrintModel.query.get(user_id)
    if relation is None or relation.fingerprint != fp:
        return Generator.gen_rest_rule(400, {}, "账号错误")
    user = relation.account
    if not Detector.check_Nick_Available(new_nick):
        return Generator.gen_rest_rule(400, {}, "用户名重复")
    user.nick = new_nick
    db.session.add(user)
    db.session.commit()
    return Generator.gen_rest_rule(200, {}, "昵称修改成功")


@userBp.route("/change/desc", methods=['POST'])
def desc_change():
    user_id = request.values.get("id")
    new_desc = request.values.get("new_desc")
    fp = request.values.get("fp")
    relation = AccountFingerPrintModel.query.get(user_id)
    if relation is None or relation.fingerprint != fp:
        return Generator.gen_rest_rule(400, {}, "账号错误")
    user = relation.account
    user.desc = new_desc
    db.session.add(user)
    db.session.commit()
    return Generator.gen_rest_rule(200, {}, "个性签名修改成功")


@userBp.route("/delete/article", methods=['POST'])
def article_delete():
    article_id = request.values.get("id")
    article = ArticleModel.query.get(article_id)
    fp = request.values.get("fp")
    if article is None:
        return Generator.gen_rest_rule(400, {}, "该文章不存在")
    relation = AccountFingerPrintModel.query.get(article.author_id)
    if relation.fingerprint != fp and relation.account.group == 0:
        return Generator.gen_rest_rule(400, {}, "无权操作")
    comments = article.comments
    likes = LikeRecordModel.query.filter_by(article_id=article_id)
    for like in likes:
        db.session.delete(like)
    for comment in comments:
        db.session.delete(comment)
    db.session.commit()
    db.session.delete(article)
    db.session.commit()
    loggerModel = LoggerModel()
    loggerModel.exec_id = relation.account.id
    loggerModel.exec_type = 3
    loggerModel.info = f"删除文章:{article_id}"
    db.session.add(loggerModel)
    db.session.commit()
    return Generator.gen_rest_rule(200, {}, "文章删除成功")


@userBp.route("/delete/comment", methods=['POST'])
def comment_delete():
    comment_id = request.values.get("id")
    comment = CommentModel.query.get(comment_id)
    fp = request.values.get("fp")
    if comment is None:
        return Generator.gen_rest_rule(400, {}, "该评论不存在")
    relation = AccountFingerPrintModel.query.get(comment.author_id)
    if relation.fingerprint != fp and relation.account.group == 0:
        return Generator.gen_rest_rule(400, {}, "无权操作")
    children_comments = comment.children_comments
    for children_comment in children_comments:
        db.session.delete(children_comment)
    db.session.delete(comment)
    db.session.commit()
    loggerModel = LoggerModel()
    loggerModel.exec_id = relation.account.id
    loggerModel.exec_type = 3
    loggerModel.info = f"删除评论:{comment.comment}"
    db.session.add(loggerModel)
    db.session.commit()
    return Generator.gen_rest_rule(200, {}, "评论删除成功")
