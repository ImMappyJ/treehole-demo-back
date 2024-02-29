import logging

from flask import Blueprint, request
from models import AccountFingerPrintModel, UserModel, ArticleModel, TypeModel, CommentModel, LikeRecordModel, \
    LoggerModel
from exts import db
from Utils import Generator

articleBp = Blueprint("article", __name__, url_prefix="/article")


@articleBp.route("/search", methods=['GET'])
def article_search():
    page = int(request.args.get('page', 1))
    max_per_page = int(request.args.get('max', 10))
    search_query = request.args.get('query', '')

    # 查询符合条件的文章，并按照 (view + 2 * like) 从高到低排序
    articles = ArticleModel.query.filter(ArticleModel.title.ilike(f'%{search_query}%')) \
        .order_by((ArticleModel.view + 2 * ArticleModel.like).desc()) \
        .paginate(page=page, per_page=max_per_page)

    article_list = []

    for article in articles.items:
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
        author_dict = {
            "nick": article.author.nick,
            "id": article.author.id
        }
        article_list.append({"article": article_dict, "author": author_dict})

    return Generator.gen_rest_rule(200, {
        'articles': article_list,
        'page': articles.page,
        'total_pages': articles.pages
    }, "搜索成功")


@articleBp.route("/like", methods=['POST'])
def article_like():
    article_id = request.values.get("id")
    user_fp = request.values.get("fp")
    try:
        relation = AccountFingerPrintModel.query.filter_by(fingerprint=user_fp).first()
        user = relation.account
        like_record = LikeRecordModel.query.filter_by(user_id=user.id, article_id=article_id).first()
        if like_record:
            return Generator.gen_rest_rule(400, {}, "重复点赞")

        else:
            article = ArticleModel.query.get(article_id)
            article.like = article.like + 1
            new_like_record = LikeRecordModel(user_id=user.id, article_id=article_id)
            db.session.add(article)
            db.session.add(new_like_record)
            db.session.commit()
            loggerModel = LoggerModel()
            loggerModel.exec_id = user.id
            loggerModel.exec_type = 0
            loggerModel.info = f"点赞文章{article_id}"
            db.session.add(loggerModel)
            db.session.commit()
            return Generator.gen_rest_rule(200, {}, "点赞成功")
    except Exception as e:
        logging.getLogger().error(str(e))
        return Generator.gen_rest_rule(400, {}, "数据错误")


@articleBp.route("/types", methods=['GET'])
def article_types():
    type_dicts = [
        {
            'id': type_element.id,
            'name': type_element.type,
        }
        for type_element in TypeModel.query.all()
    ]
    return Generator.gen_rest_rule(200, {
        "types": type_dicts
    }, "获取成功")


@articleBp.route("/post", methods=['POST'])
def article_post():
    data = request.get_json()
    article_title = data.get('title')
    article_type = data.get('type')
    fingerprint = data.get('fp')
    if TypeModel.query.get(article_type) is None:
        return Generator.gen_rest_rule(400, {}, "分类不存在")
    article_context = data.get('context')

    relation = AccountFingerPrintModel.query.filter_by(fingerprint=fingerprint).first()
    if relation is None:
        return Generator.gen_rest_rule(400, {}, "用户不存在")

    author = relation.account
    article = ArticleModel()
    article.author_id = author.id
    article.title = article_title
    article.type_id = article_type
    article.context = article_context
    db.session.add(article)
    db.session.commit()
    loggerModel = LoggerModel()
    loggerModel.exec_id = author.id
    loggerModel.exec_type = 4
    loggerModel.info = f"发布文章{article.id}"
    db.session.add(loggerModel)
    db.session.commit()
    return Generator.gen_rest_rule(200, {
        'article_id': article.id
    }, "发表成功")


@articleBp.route("/get/all", methods=['GET'])
def article_get_all():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    articles = ArticleModel.query.order_by(ArticleModel.id.desc()).paginate(page=page, per_page=per_page)
    article_list = []

    for article in articles.items:
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
        author_dict = {
            "nick": article.author.nick,
            "id": article.author.id
        }
        article_list.append({"article": article_dict, "author": author_dict})

    return Generator.gen_rest_rule(200, {
        'articles': article_list,
        'page': articles.page,
        'total_pages': articles.pages
    }, "获取成功")


@articleBp.route("/get/byid", methods=['GET'])
def article_get_byid():
    article_id = request.args.get("id")
    article = ArticleModel.query.filter_by(id=article_id).first()
    if article is None:
        return Generator.gen_rest_rule(400, {}, "文章不存在")

    article.view = article.view + 1

    db.session.add(article)
    db.session.commit()

    comment_number = len(article.comments)

    return Generator.gen_rest_rule(200, {
        "article": {
            "id": article.id,
            "post_time": article.post_time,
            "type": article.type.type,
            "title": article.title,
            "context": article.context,
            "view": article.view,
            "like": article.like,
            "comment": comment_number
        },
        "author": {
            "nick": article.author.nick,
            "id": article.author.id
        }
    }, "成功找到文章")


@articleBp.route("/rank", methods=['GET'])
def article_rank():
    page = int(request.args.get('page', 1))
    max_per_page = int(request.args.get('per_page', 10))

    articles = ArticleModel.query.order_by((ArticleModel.view + 2 * ArticleModel.like).desc()) \
        .paginate(page=page, per_page=max_per_page)

    article_list = []

    for article in articles.items:
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
        author_dict = {
            "nick": article.author.nick,
            "id": article.author.id
        }
        article_list.append({"article": article_dict, "author": author_dict})

    return Generator.gen_rest_rule(200, {
        'articles': article_list,
        'page': articles.page,
        'total_pages': articles.pages
    }, "搜索成功")
