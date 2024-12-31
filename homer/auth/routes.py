from urllib.parse import urlsplit

import sqlalchemy as sqa
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from homer import db
from homer.auth import bp
from homer.auth.forms import LoginForm
from homer.models import User


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sqa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Někde bude asi překlep.")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/login.html", title="Přihlášení", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))
