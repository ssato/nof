#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
"""Views.
"""
import flask

from .globals import APP
from ..main import utils
from ..lib import fortios


@APP.route("/firewall", methods=["GET"])
def firewall_index():
    """Firewall index page
    """
    config_upload_url = flask.url_for("app.config_upload")

    fns = [(fn, flask.url_for(".firewall_policies",
                              filename=fn))
           for fn in utils.list_filenames("fortios_*_firewall.json")]

    return flask.render_template("fortios_firewall_index.html",
                                 filenames=fns,
                                 config_upload_url=config_upload_url)


@APP.route("/firewall/<path:filename>", methods=["GET"])
def firewall_policies(filename):
    """Firewall polices search page.
    """
    url = flask.url_for("fortios_api.get_group_config_file",
                        group="firewall", filename=filename)
    return flask.render_template("fortios_firewall.html",
                                 policies_url=url,
                                 policies_keys=fortios.FIREWALL_KEYS)

# vim:sw=4:ts=4:et:
