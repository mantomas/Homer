from datetime import datetime
from typing import Optional
from urllib import parse

from markdown import markdown
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


class Page(db.Model):
    id: sqo.Mapped[int] = sqo.mapped_column(primary_key=True)
    title: sqo.Mapped[str] = sqo.mapped_column(sqa.String(140))
    url_suffix: sqo.Mapped[str] = sqo.mapped_column(sqa.String(30), unique=True)
    body: sqo.Mapped[str] = sqo.mapped_column(sqa.Text)
    body_html: sqo.Mapped[str] = sqo.mapped_column(sqa.Text)
    author_id: sqo.Mapped[int] = sqo.mapped_column(sqa.ForeignKey(User.id))
    last_edited: sqo.Mapped[datetime] = sqo.mapped_column(
        sqa.DateTime, default=datetime.now
    )
    last_edit_by: sqo.Mapped[int] = sqo.mapped_column(sqa.ForeignKey(User.id))

    def __repr__(self):
        return "<Page {}>".format(self.title)

    @sqo.validates("author_id")
    def validate_author(self, key, value):
        if self.author_id and self.author_id != value:
            raise ValueError("Nelze měnit autora.")
        return value

    @sqo.validates("url_suffix")
    def validate_url_suffix(self, key, value):
        if value != parse.quote(value):
            raise ValueError("URL část musí být url-safe.")
        if len(value) > 30:
            raise ValueError("URL část může být maximálně 30 znaků dlouhá.")
        if "/" in value:
            raise ValueError("URL část nesmí obsahovat lomítka.")
        return value

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = markdown(value, output_format="html")


db.event.listen(Page.body, "set", Page.on_changed_body)
