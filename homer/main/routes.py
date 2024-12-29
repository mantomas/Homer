from flask import render_template

from homer.main import bp


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html")


@bp.route("/status")
def status():
    return render_template("health.html", title="Status")
