#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Views.
"""
import flask

from .. import libs
from . import common, forms


APP = flask.Blueprint("forti_app", __name__, url_prefix=common.PREFIX)

IDX_PATH = "/"
HOST_FW_PATH = "/firewall/policies/<string:hostname>/"

# .. seealso:: https://datatables.net/reference/option/columns.orderable
FIREWALL_COLS = (dict(key="edit", width="3%", orderable=False),
                 dict(key="srcaddr", width="8%"),
                 dict(key="srcintf", width="8%"),
                 dict(key="dstaddr", width="8%"),
                 dict(key="dstintf", width="8%"),
                 dict(key="service", width="8%"),
                 dict(key="status", width="4%"),
                 dict(key="action", width="4%"),
                 dict(key="comments", width="8%"),
                 dict(key="srcaddrs", width="12%"),
                 dict(key="dstaddrs", width="12%"))

_CNF_LABELS = {libs.FORTI_CNF_ALL: "all configuration",
               libs.FORTI_CNF_META: "metadata",
               libs.FORTI_FIREWALL_POLICIES_RESOLVED: "firewall policies"
               }


def cnf_urls_itr(host_cnfs, cnf_labels=_CNF_LABELS):
    """
    :param host_cnfs: A mapping object gives hostname and config filenames
    """
    hname = host_cnfs["hostname"]
    for fname in host_cnfs["filenames"]:
        label = cnf_labels.get(fname, False)
        if label:
            yield (
                label,
                flask.url_for("forti_api.get_host_config",
                              hostname=hname, filename=fname)
            )


@APP.route(IDX_PATH, methods=["GET", "POST"])
def index():
    """Fortios nodes index page.
    """
    form = forms.UploadFortiShowConfigForm()

    # [{"hostname": ...,  "filenames": [...]}]
    h_cnfs = [(d["hostname"], list(cnf_urls_itr(d)),
               flask.url_for(".host_firewall_policies",
                             hostname=d["hostname"]))
              for d in common.list_hosts_with_data_filenames()]

    ctx = dict(form=form, hosts_with_filenames=h_cnfs,
               summary="Fortios Index")

    if flask.request.method == "POST" and form.validate_on_submit():
        try:
            payload = form.upload.data
            common.upload_forti_show_config(payload.filename,
                                            payload.read())
            msg = u"File was successfully uploaded."

        except RuntimeError as exc:
            msg = u"Failed to upload: {}".format(payload.filename)
            flask.current_app.logger.warn(
                msg + " {!r}".format(exc)
            )

        return flask.redirect(flask.url_for(".index", msg=msg, **ctx))

    return flask.render_template("fortios_index.html", **ctx)


@APP.route(HOST_FW_PATH, methods=["GET"])
def host_firewall_policies(hostname):
    """Host's firewall policy page.
    """
    summary = "Host {}: Firewall Policies".format(hostname)
    purl = flask.url_for("forti_api.get_host_config",
                         hostname=hostname,
                         filename=libs.FORTI_FIREWALL_POLICIES_RESOLVED)

    return flask.render_template("fortios_host_firewall_policies.html",
                                 summary=summary, hostname=hostname,
                                 policies_url=purl,
                                 policies_cols=FIREWALL_COLS,)

# vim:sw=4:ts=4:et:
