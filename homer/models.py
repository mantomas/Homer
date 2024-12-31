from typing import Optional

import sqlalchemy as sqa
import sqlalchemy.orm as sqo
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from homer import db, login


class User(UserMixin, db.Model):
    id: sqo.Mapped[int] = sqo.mapped_column(primary_key=True)
    username: sqo.Mapped[str] = sqo.mapped_column(
        sqa.String(64), index=True, unique=True
    )
    password_hash: sqo.Mapped[Optional[str]] = sqo.mapped_column(sqa.String(256))

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
