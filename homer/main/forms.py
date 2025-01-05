from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class PageForm(FlaskForm):
    title = StringField("Titulek", validators=[DataRequired()])
    url_suffix = StringField(
        "URL (30), bude vidět také v menu",
        validators=[DataRequired()],
    )
    body = PageDownField("Obsah stránky v Markdown?", validators=[DataRequired()])
    submit = SubmitField("Submit")
