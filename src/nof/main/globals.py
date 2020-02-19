#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
"""Globals
"""
import flask


API_PREFIX = "/api/v1"

APP = flask.Blueprint("app", __name__)
API = flask.Blueprint("api", __name__, url_prefix=API_PREFIX)

# vim:sw=4:ts=4:et:
