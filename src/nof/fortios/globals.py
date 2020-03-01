#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
"""Globals
"""
import flask


_PREFIX = "/fortios"
_API_PREFIX = _PREFIX + "/api/v1"

APP = flask.Blueprint("fortios_app", __name__, url_prefix=_PREFIX)
API = flask.Blueprint("fortios_api", __name__, url_prefix=_API_PREFIX)

# vim:sw=4:ts=4:et:
