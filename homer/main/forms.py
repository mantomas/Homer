from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    StringField,
    SubmitField,
    SelectField,
    widgets,
)
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class PageForm(FlaskForm):
    title = StringField("Titulek", validators=[DataRequired()])
    url_suffix = StringField(
        "URL (30), bude vidět také v menu",
        validators=[DataRequired()],
    )
    body = PageDownField("Obsah stránky v Markdown?", validators=[DataRequired()])
    submit = SubmitField("Uložit")


class FloatRangeField(FloatField):
    widget = widgets.RangeInput()


class HeatingForm(FlaskForm):
    burn_date = DateField(
        "Datum",
        default=date.today(),
        validators=[
            DataRequired("Zadej datum ve formátu dd/mm/rrrr nebo použij kalendář")
        ],
    )
    weight_choices = [6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13]
    weight = SelectField(
        "Váha dřeva",
        choices=weight_choices,
        validators=[DataRequired()],
    )
    temperature_in = FloatRangeField("Teplota uvnitř", validators=[])
    temperature_out = FloatRangeField("Teplota venku", validators=[])
    note = StringField("Poznámka")
    submit = SubmitField("Uložit")
