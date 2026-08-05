"""Test configs."""


import pytest

from xl_auth.app import create_app
from xl_auth.settings import DevConfig, ProdConfig


def test_production_config(monkeypatch):
    """Production config."""
    monkeypatch.setenv('XL_AUTH_SECRET', 'a-real-secret')
    app = create_app(ProdConfig)
    assert app.config['ENV'] == 'prod'
    assert app.config['DEBUG'] is False
    assert app.config['DEBUG_TB_ENABLED'] is False
    assert app.config['SECRET_KEY'] == 'a-real-secret'


def test_production_config_refuses_default_secret(monkeypatch):
    """Production refuses to start without an explicit secret."""
    monkeypatch.delenv('XL_AUTH_SECRET', raising=False)
    with pytest.raises(RuntimeError, match='XL_AUTH_SECRET must be set'):
        create_app(ProdConfig)


def test_dev_config():
    """Development config."""
    app = create_app(DevConfig)
    assert app.config['ENV'] == 'dev'
    assert app.config['DEBUG'] is True
