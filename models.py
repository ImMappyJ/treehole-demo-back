from exts import db
from datetime import datetime


class UserModel(db.Model):
    __tablename__ = "db_user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nick = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)  # 使用SHA256加密，长度为64
    email = db.Column(db.String(50), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)
    desc = db.Column(db.String(100), nullable=False, default="我是超级懒狗")
    group = db.Column(db.Integer, default=0)  # 0 为普通用户 1 为管理员


class EmailVerifyCodeModel(db.Model):
    __tablename__ = "db_email_verify_code"
    email = db.Column(db.String(20), nullable=False, primary_key=True)
    send_time = db.Column(db.DateTime, default=datetime.now)
    code = db.Column(db.String(10), nullable=False)
    isused = db.Column(db.Boolean, default=False)


class AccountFingerPrintModel(db.Model):
    __tablename__ = "db_account_fingerprint"
    fingerprint = db.Column(db.String(64), nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('db_user.id'), nullable=False, unique=True, primary_key=True)
    gen_time = db.Column(db.DateTime, default=datetime.now)
    account = db.relationship("UserModel")


class TypeModel(db.Model):
    __tablename__ = "db_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    type = db.Column(db.String(30), nullable=False, default="未命名")
    articles = db.relationship('ArticleModel', backref='type')


class ArticleModel(db.Model):
    __tablename__ = "db_post_articles"
    title = db.Column(db.String(30), nullable=False)
    post_time = db.Column(db.DateTime, default=datetime.now)
    type_id = db.Column(db.Integer, db.ForeignKey('db_type.id'), nullable=False, default=0)
    context = db.Column(db.Text(65536), nullable=False)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("db_user.id"), nullable=False)
    author = db.relationship("UserModel", backref=db.backref("articles"))
    view = db.Column(db.Integer, nullable=False, default=0)
    like = db.Column(db.Integer, nullable=False, default=0)
    comments = db.relationship("CommentModel", backref=db.backref("article"))


class CommentModel(db.Model):
    __tablename__ = "db_comments"
    author_id = db.Column(db.Integer, db.ForeignKey('db_user.id'), nullable=False)
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('db_post_articles.id'), nullable=False)
    post_time = db.Column(db.DateTime, default=datetime.now)
    comment = db.Column(db.Text, nullable=False)
    author = db.relationship("UserModel", backref=db.backref("comments"))
    father_comment_id = db.Column(db.Integer, db.ForeignKey("db_comments.comment_id"), nullable=True)
    father_comment = db.relationship("CommentModel", backref=db.backref("children_comments"), remote_side=[comment_id])


class LikeRecordModel(db.Model):
    __tablename__ = "db_like_records"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('db_user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('db_post_articles.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'article_id'),)


class LoggerModel(db.Model):
    __tablename__ = "db_logger"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exec_time = db.Column(db.DateTime, default=datetime.now())
    exec_id = db.Column(db.Integer, db.ForeignKey("db_user.id"), nullable=False)
    exec_type = db.Column(db.Integer, nullable=False, default=0)  # 0 为普通日志 1 为登录 2 为登出 3 为删除操作 4 为发布操作
    info = db.Column(db.String(100), default="无信息")
