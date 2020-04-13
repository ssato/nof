#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Views.
"""
import flask

from . import globals, utils


APP = flask.Blueprint("fortios_app", __name__, url_prefix=globals.PREFIX)

FIREWALL_POLICY_FILENAME = "firewall_policy.json"

FIREWALL_COLS = (dict(key="edit"),
                 dict(key="srcaddr", width="12%"),
                 dict(key="srcintf", width="10%"),
                 dict(key="dstaddr", width="12%"),
                 dict(key="dstintf", width="10%"),
                 dict(key="service", width="10%"),
                 dict(key="status", width="5%"),
                 dict(key="action", width="5%"),
                 dict(key="comments", width="8%"))


@APP.route("/", methods=["GET"])
def index():
    """Fortios nodes index page.
    """
    # [{"hostname": ...,  "filenames": [...]}]
    h_cnfs = [(d["hostname"],
               flask.url_for(".host_details", hostname=d["hostname"]),
               d["filenames"],
               flask.url_for(".host_firewall_policies",
                             hostname=d["hostname"]))
              for d in utils.list_hosts_with_config_filenames()]

    config_upload_url = flask.url_for("app.config_index")

    return flask.render_template("fortios_index.html",
                                 hosts_with_filenames=h_cnfs,
                                 config_upload_url=config_upload_url)


@APP.route("/<string:hostname>", methods=["GET"])
def host_details(hostname):
    """Host's details page.
    """
    cnfs = [(fn,
             flask.url_for("fortios_api.get_host_config",
                           hostname=hostname, filename=fn))
            for fn in utils.list_host_configs(hostname)]

    purl = flask.url_for(".host_firewall_policies", hostname=hostname)

    return flask.render_template("fortios_host.html",
                                 hostname=hostname,
                                 summary="Fortios Node Details",
                                 configs=cnfs, policies_url=purl)


@APP.route("/<string:hostname>/firewall_policies", methods=["GET"])
def host_firewall_policies(hostname):
    """Host's firewall policy page.
    """
    summary = "Host {}: Firewall Policies".format(hostname)
    purl = flask.url_for("fortios_api.get_host_config",
                         hostname=hostname, filename=FIREWALL_POLICY_FILENAME)
    curls = [flask.url_for("fortios_api.get_host_config",
                           hostname=hostname, filename=f)
             for f in utils.list_host_configs(hostname)]

    return flask.render_template("fortios_host_firewall_policies.html",
                                 summary=summary, hostname=hostname,
                                 config_urls=curls, policies_url=purl,
                                 policies_cols=FIREWALL_COLS,)

# vim:sw=4:ts=4:et:
