#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
r"""Initialize this app.
"""
import flask
import flask_bootstrap
import flask_wtf.csrf

from . import config, main, networks, fortios


def create_app(cnf_name="development"):
    """
    :param cnf_name: Config name, e.g. "development"
    """
    cnf = config.get_config(cnf_name)

    app = flask.Flask(__name__)
    app.config.from_object(cnf)
    cnf.init_app(app)

    bootstrap = flask_bootstrap.Bootstrap()
    bootstrap.init_app(app)

    csrf = flask_wtf.csrf.CSRFProtect()
    csrf.init_app(app)

    app.register_blueprint(main.APP)

    app.register_blueprint(networks.APP)
    app.register_blueprint(networks.API)

    app.register_blueprint(fortios.APP)
    app.register_blueprint(fortios.API)

    return app

# vim:sw=4:ts=4:et:
