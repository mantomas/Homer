from unittest.mock import MagicMock, patch

from config import Config
from homer import create_app


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@patch("os.path.exists", MagicMock(return_value=False))
@patch("os.mkdir")
def test_app_creation(mock_mkdir: MagicMock):
    app = create_app(TestConfig)
    assert app is not None
    assert app.config["SECRET_KEY"] != ""
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    mock_mkdir.assert_called_once_with("logs")


def test_app_blueprints(app):
    assert "errors" in app.blueprints
    assert "main" in app.blueprints
    assert "auth" in app.blueprints


def test_app_logging(app):
    assert app.logger is not None
