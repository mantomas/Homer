from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    StringField,
    SubmitField,
    SelectField,
    widgets,
)
from wtforms.validators import InputRequired, NumberRange
from flask_pagedown.fields import PageDownField


class PageForm(FlaskForm):
    title = StringField("Titulek", validators=[InputRequired()])
    url_suffix = StringField(
        "URL (30), bude vidět také v menu",
        validators=[InputRequired()],
    )
    body = PageDownField("Obsah stránky v Markdown?", validators=[InputRequired()])
    submit = SubmitField("Uložit")


class FloatRangeField(FloatField):
    widget = widgets.RangeInput()


class HeatingForm(FlaskForm):
    burn_date = DateField(
        "Datum",
        validators=[
            InputRequired("Zadej datum ve formátu dd/mm/rrrr nebo použij kalendář")
        ],
    )
    weight_choices = [6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13]
    weight = SelectField(
        "Váha dřeva",
        choices=weight_choices,
        validators=[InputRequired()],
    )
    temperature_in = FloatField(
        "Teplota uvnitř",
        validators=[
            InputRequired("Zadej teplotu uvnitř"),
            NumberRange(0, 25, "Ta teplota uvnitř se mi nezdá."),
        ],
    )
    temperature_out = FloatField(
        "Teplota venku",
        validators=[
            InputRequired("zadej teplotu venku"),
            NumberRange(-80, 40, "Ta teplota venku se mi nezdá."),
        ],
    )
    note = StringField("Poznámka")
    submit = SubmitField("Uložit")
