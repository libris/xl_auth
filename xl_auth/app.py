# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask, render_template
from flask_login import current_user

from . import collection, commands, oauth, permission, public, user
from .extensions import (babel, bcrypt, cache, csrf_protect, db, debug_toolbar, login_manager,
                         migrate, oauth_provider, webpack)
from .settings import ProdConfig


def create_app(config_object=ProdConfig):
    """An application factory, explained here: http://flask.pocoo.org/docs/patterns/appfactories/ .

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_after_request_funcs(app)
    register_shell_context(app)
    register_commands(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    babel.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    oauth_provider.init_app(app)
    webpack.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(collection.views.blueprint)
    app.register_blueprint(permission.views.blueprint)
    app.register_blueprint(oauth.views.blueprint)
    app.register_blueprint(oauth.client.views.blueprint)
    app.register_blueprint(oauth.grant.views.blueprint)
    app.register_blueprint(oauth.token.views.blueprint)
    return None


def register_error_handlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template('{0}.html'.format(error_code)), error_code

    for errcode in [403, 404, 429, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_after_request_funcs(app):
    """Register after-request functions."""
    def add_x_username_header(response):
        """Add X-Username header when authenticated."""
        if current_user.is_authenticated:
            response.headers['X-Username'] = current_user.email
        return response

    app.after_request_funcs.setdefault(None, [])
    app.after_request_funcs[None].append(add_x_username_header)


def register_shell_context(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {'db': db, 'User': user.models.User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.translate)
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.create_user)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.import_data)
