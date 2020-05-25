#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Views for networks app.
"""
import itertools
import os.path
import os

import flask

from ..globals import FT_NETWORKS
from .. import libs, utils
from . import forms
from .common import PREFIX


APP = flask.Blueprint("networks_app", __name__, url_prefix=PREFIX)

SUMMARIES = dict(index=u"NOF",
                 finder=u"Find Network Objects")

TEMPLATES = dict(index="networks_index.html",
                 find_nets="networks_find_networks.html",
                 find_paths="networks_find_paths.html")

# url prefixes:
IDX_PATH = "/"
FIND_NETS_PATH = os.path.join("/by_addr", "<path:filename>")
FIND_PATHS_PATH = os.path.join("/by_path", "<path:filename>")


@APP.route(IDX_PATH, methods=["GET", "POST"])
def index():
    """
    Networks index page show the list of uploaded networks files and form to
    upload them.
    """
    form = forms.UploadNetworksForm()
    tmpl = TEMPLATES["index"]
    summary = SUMMARIES["index"]
    ftype = FT_NETWORKS

    filename = None  # It will be set.
    filenames = utils.list_uploaded_filenames(ftype, "*.json")
    octxs = dict(form=form, filenames=filenames, summary=summary)

    if form.validate_on_submit():
        ndata = form.upload.data
        ndata.seek(0)
        content = ndata.read().decode("utf-8")
        fpath = utils.uploaded_filepath(ndata.filename, ftype,
                                        content=content)
        filename = os.path.basename(fpath)

        utils.ensure_dir_exists(fpath)
        # ndata.save() does not work as expected
        open(fpath, 'w').write(content)

        msg = u"File was successfully uploaded."
        return flask.render_template(tmpl, filename=filename, msg=msg, **octxs)

    return flask.render_template(tmpl, filename=filename, **octxs)


@APP.route(FIND_NETS_PATH, methods=['GET', 'POST'])
def find_networks(filename):
    """Find networks for given IP address.
    """
    form = forms.FindNetworksForm(flask.request.form)
    summary = SUMMARIES["finder"]
    tmpl = TEMPLATES["find_nets"]

    nlink_url = flask.url_for("networks_api.get_or_upload_networks",
                              filename=filename)
    nets = []
    node_paths = []

    octxs = dict(form=form, filename=filename, summary=summary)

    if form.validate_on_submit():
        ipa = form.ipa.data
        nets = libs.find_networks_by_ipaddr(filename, ipa)

    return flask.render_template(tmpl, nets=nets, node_link_url=nlink_url,
                                 node_paths=node_paths, **octxs)


@APP.route(FIND_PATHS_PATH, methods=['GET', 'POST'])
def find_network_paths(filename):
    """Find networks for given IP address.
    """
    form = forms.FindNetworkPathsForm(flask.request.form)
    summary = SUMMARIES["finder"]
    tmpl = TEMPLATES["find_paths"]

    nlink_url = flask.url_for("networks.api.get_or_upload_networks",
                              filename=filename)
    nets = []
    node_paths = []

    octxs = dict(form=form, filename=filename, summary=summary)

    if form.validate_on_submit():
        src_ip = form.src_ip.data
        dst_ip = form.dst_ip.data
        ntype = form.node_type.data
        node_paths = libs.find_network_paths(filename, src_ip, dst_ip,
                                             node_type=ntype)
        nets = list(set(itertools.chain.from_iterable(node_paths)))

    return flask.render_template(tmpl, nets=nets, node_link_url=nlink_url,
                                 node_paths=node_paths, **octxs)

# vim:sw=4:ts=4:et:
