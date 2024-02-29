from models import UserModel


def check_Nick_Available(newname):
    user = UserModel.query.filter_by(nick=newname).first()
    return user is None
