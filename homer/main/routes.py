from flask import render_template
from flask_login import current_user, login_required

from homer.main import bp


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/status")
@login_required
def status():
    return render_template("health.html", title="Status", current_user=current_user)
