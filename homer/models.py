from datetime import date, datetime
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


class Heating(db.Model):
    id: sqo.Mapped[int] = sqo.mapped_column(primary_key=True)
    weight: sqo.Mapped[float] = sqo.mapped_column(sqa.Float, nullable=False)
    burn_date: sqo.Mapped[datetime] = sqo.mapped_column(sqa.Date, nullable=False)
    temperature_in: sqo.Mapped[float] = sqo.mapped_column(sqa.Float)
    temperature_out: sqo.Mapped[float] = sqo.mapped_column(sqa.Float)
    note: sqo.Mapped[str] = sqo.mapped_column(sqa.String(500))
    season: sqo.Mapped[str] = sqo.mapped_column(sqa.String(10))

    def __repr__(self):
        return "<Heating record {}>".format(self.burn_date)

    @sqo.validates("weight")
    def validate_weight(self, key, value):
        if not 5.0 < float(value) < 14.0:
            raise ValueError("Do kamen patří 6 až 12 kg dřeva.")
        return value

    @sqo.validates("burn_date")
    def validate_burn_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError("Datum je ve špatném formátu.")

        if value > date.today():
            raise ValueError("Nemůžeš topit v budoucnosti.")

        same_day_records = db.session.execute(
            db.select(Heating).where(Heating.burn_date == value)
        ).scalars()
        same_day_ids = [r.id for r in same_day_records]
        if not self.id and len(same_day_ids) > 1:
            # cannot create new record for the same day
            raise ValueError("Maximálně 2 topení za den.")
        if self.id not in same_day_ids and len(same_day_ids) > 1:
            # cannot update record to the day with 2 or more records
            burn_date = value.strftime("%d.%m.%Y")
            raise ValueError(f"Pro {burn_date} už jsou {len(same_day_ids)} záznamy.")

        return value

    @sqo.validates("temperature_in")
    def validate_temperature_in(self, key, value):
        if not 0.0 < float(value) < 25.0:
            raise ValueError("Předpokládám teplotu uvnitř mezi 1 až 25 °C.")
        return value

    @sqo.validates("temperature_out")
    def validate_temperature_out(self, key, value):
        if not -80.0 < float(value) < 40.0:
            raise ValueError(f"Apokalypsa nastala, když je venku {value} °C.")
        return value

    @staticmethod
    def set_season(target, value, oldvalue, initiator):
        """
        Set season based on burn_date
        Season last from 1.7. to 30.6.
        Format is "YYYY-XXXX" e.g "2020-2021"
        """
        if value.month < 7:
            target.season = f"{value.year - 1}-{value.year}"
        else:
            target.season = f"{value.year}-{value.year + 1}"


db.event.listen(Heating.burn_date, "set", Heating.set_season)
