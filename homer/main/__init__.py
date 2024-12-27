from flask import Blueprint

bp = Blueprint("main", __name__)

from homer.main import routes  # noqa
