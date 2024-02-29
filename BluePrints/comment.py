import logging
from flask import Blueprint, request
from exts import db
from models import ArticleModel, CommentModel, AccountFingerPrintModel, LoggerModel
from Utils import Generator

commentBp = Blueprint("comment", __name__, url_prefix="/comment")


@commentBp.route("/post", methods=['POST'])
def post_comment():
    author_fp = request.values.get("fp")
    comment = request.values.get("comment")
    article_id = request.values.get("article")
    father_comment_id = request.values.get("father_comment")

    try:
        comment_model = CommentModel()
        comment_model.comment = comment
        comment_model.article_id = article_id
        if father_comment_id:
            father_comment = CommentModel.query.get(father_comment_id)
            if father_comment.father_comment is not None:
                return Generator.gen_rest_rule(400, {}, "目标评论错误")
            comment_model.father_comment_id = father_comment_id
        relation = AccountFingerPrintModel.query.filter_by(fingerprint=author_fp).first()
        author = relation.account
        comment_model.author_id = author.id
        db.session.add(comment_model)
        db.session.commit()
        loggerModel = LoggerModel()
        loggerModel.exec_id = relation.account.id
        loggerModel.exec_type = 3
        loggerModel.info = "发布评论:" + comment
        db.session.add(loggerModel)
        db.session.commit()
    except Exception as e:
        logging.getLogger().error(str(e))
        return Generator.gen_rest_rule(400, {}, "数据错误")
    return Generator.gen_rest_rule(200, {
        'comment_id': comment_model.comment_id
    }, "发送成功")


@commentBp.route("/get/by/id", methods=['GET'])
def get_comments_by_id():
    comment_id = request.args.get("id")
    comment = CommentModel.query.filter_by(comment_id=comment_id).first()
    if comment is None:
        return Generator.gen_rest_rule(400, {}, "评论不存在")

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    # 查询指定评论的子评论，并按照时间倒序排列
    children_comments_query = CommentModel.query.filter_by(father_comment_id=comment_id).order_by(CommentModel.post_time)

    # 使用 paginate() 方法进行分页
    paginated_comments = children_comments_query.paginate(page=page, per_page=per_page, error_out=False)

    # 构造返回结果
    comments_list = []
    for child_comment in paginated_comments.items:
        child_comment_dict = {
            "comment_id": child_comment.comment_id,
            "comment": child_comment.comment,
            "post_time": child_comment.post_time,
            "author": {
                "nick": child_comment.author.nick,
                "desc": child_comment.author.desc,
                "id": child_comment.author.id
            }
        }
        comments_list.append(child_comment_dict)

    return Generator.gen_rest_rule(200, {
        "comments": comments_list,
        "total": paginated_comments.total,
        "pages": paginated_comments.pages,
        "has_prev": paginated_comments.has_prev,
        "has_next": paginated_comments.has_next
    }, "成功获取子评论")


@commentBp.route("/get/by/article", methods=['GET'])
def get_comments_by_article_id():
    article_id = request.args.get("id")
    article = ArticleModel.query.filter_by(id=article_id).first()
    if article is None:
        return Generator.gen_rest_rule(400, {}, "文章不存在")

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    comments_query = CommentModel.query.filter_by(article_id=article_id, father_comment_id=None).order_by(CommentModel.post_time)

    paginated_comments = comments_query.paginate(page=page, per_page=per_page, error_out=False)

    # 构造返回结果
    comments_list = []
    for comment in paginated_comments.items:
        comment_dict = {
            "comment_id": comment.comment_id,
            "comment": comment.comment,
            "post_time": comment.post_time,
            "author": {
                "nick": comment.author.nick,
                "desc": comment.author.desc,
                "id": comment.author.id
            }
        }
        comments_list.append(comment_dict)

    return Generator.gen_rest_rule(200, {
        "comments": comments_list,
        "total": paginated_comments.total,
        "pages": paginated_comments.pages,
        "has_prev": paginated_comments.has_prev,
        "has_next": paginated_comments.has_next
    }, "成功获取评论")
