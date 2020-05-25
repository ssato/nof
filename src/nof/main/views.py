#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Views for the main app.
"""
import flask


APP = flask.Blueprint("main", __name__)


@APP.route("/", methods=["GET"])
def index():
    """
    Networks index page show the list of uploaded networks files and form to
    upload them.
    """
    tmpl = "top.html"
    return flask.render_template(tmpl)

# vim:sw=4:ts=4:et:
