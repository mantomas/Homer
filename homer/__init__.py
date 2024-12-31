import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = "Tady je potřeba přihlášení."


def create_app(config_class=Config) -> Flask:
    homer = Flask(__name__)
    homer.config.from_object(config_class)

    db.init_app(homer)
    migrate.init_app(homer, db)
    login.init_app(homer)

    from homer.errors import bp as errors_bp

    homer.register_blueprint(errors_bp)

    from homer.main import bp as main_bp

    homer.register_blueprint(main_bp)

    from homer.auth import bp as auth_bp

    homer.register_blueprint(auth_bp, url_prefix="/auth")

    if not homer.debug and not homer.testing:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler("logs/homer", maxBytes=10240, backupCount=10)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        homer.logger.addHandler(file_handler)

        homer.logger.setLevel(logging.INFO)
        homer.logger.info("Homer startup!")

    return homer
