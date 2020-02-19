#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
r"""Entrypoint of this app.
"""
import flask
import flask_bootstrap
import flask_wtf.csrf

from . import config, main


def create_app(cnf_name="development"):
    """
    :param cnf_name: Config name, e.g. "development"
    """
    cnf = config.CNF[cnf_name]

    app = flask.Flask(__name__)
    app.config.from_object(cnf)
    cnf.init_app(app)

    bootstrap = flask_bootstrap.Bootstrap()
    bootstrap.init_app(app)

    csrf = flask_wtf.csrf.CSRFProtect()
    csrf.init_app(app)

    app.register_blueprint(main.APP)
    app.register_blueprint(main.API)

    return app

# vim:sw=4:ts=4:et:
