from flask import Blueprint

bp = Blueprint("auth", __name__)

from homer.auth import routes  # noqa
