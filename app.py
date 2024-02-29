from flask import Flask
from flask_cors import CORS
from exts import db, mail
from flask_migrate import Migrate
from BluePrints import authBp, verifyBp, articleBp, userBp, commentBp
import config

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.from_object(config)

db.init_app(app)
mail.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(authBp)
app.register_blueprint(verifyBp)
app.register_blueprint(articleBp)
app.register_blueprint(userBp)
app.register_blueprint(commentBp)

if __name__ == "__main__":
    app.run(debug=True)
