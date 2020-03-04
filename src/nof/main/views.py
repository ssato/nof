#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Views.
"""
import itertools
import os.path
import os

import flask

from .forms import (
    UploadForm, NetworkFinderForm, PathFinderForm, ConfigUploadForm
)
from .utils import (
    upload_filepath, generate_node_link_data_from_graph_data, list_filenames,
    find_networks_from_graph, find_paths_from_graph, parse_config_and_save,
    utils, is_valid_config_type
)
from ..globals import NODE_ANY, CONFIG_TYPES


APP = flask.Blueprint("app", __name__)

SUMMARIES = dict(index=u"NOF",
                 upload=u"Upload Network Graph data",
                 finder=u"Find Network Objects")


@APP.route("/", methods=["GET"])
def index():
    """Top page.
    """
    filenames = list_filenames("*.yml")
    return flask.render_template("index.html", filenames=filenames)


@APP.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload page.
    """
    form = UploadForm()
    filename = None
    octxs = dict(form=form, summary=SUMMARIES["upload"])

    if form.validate_on_submit():
        yml_data = form.upload.data
        filepath = upload_filepath(yml_data.filename)
        filename = os.path.basename(filepath)
        yml_data.save(filepath)

        try:
            generate_node_link_data_from_graph_data(filename)
        except (IOError, OSError, ValueError, RuntimeError):
            flask.flash(u"Failed to convert the YAML data uploaded! "
                        u"Please try again with other valid data files.")
            return flask.render_template("upload.html", **octxs)

        flask.flash(u"File was successfully uploaded and converted.")
        return flask.redirect(flask.url_for(".index", filename=filename))

    return flask.render_template("upload.html", filename=filename, **octxs)


@APP.route("/finder/networks/<path:filename>", methods=['GET', 'POST'])
def network_finder(filename):
    """Find networks for given IP address.
    """
    form = NetworkFinderForm(flask.request.form)

    nlink_url = flask.url_for("api.get_node_link", filename=filename)
    networks = []

    if form.validate_on_submit():
        ip = form.ip.data
        networks = find_networks_from_graph(filename, ip)

    return flask.render_template("finder_network.html", form=form,
                                 filename=filename, networks=networks,
                                 node_link_url=nlink_url,
                                 summary=SUMMARIES["finder"])


@APP.route("/finder/paths/<path:filename>", methods=['GET', 'POST'])
def path_finder(filename):
    """Page to find objects.
    """
    form = PathFinderForm(flask.request.form)

    nlink_url = flask.url_for("api.get_node_link", filename=filename)
    node_type = NODE_ANY
    node_paths = []

    if form.validate_on_submit():
        src = form.src_ip.data
        dst = form.dst_ip.data
        node_type = form.find_type.data
        node_paths = find_paths_from_graph(filename, src, dst,
                                           node_type=node_type)

    return flask.render_template("finder.html", form=form,
                                 filename=filename,
                                 node_link_url=nlink_url,
                                 node_paths=node_paths,
                                 node_type=node_type,
                                 summary=SUMMARIES["finder"])


@APP.route("/config", methods=["GET"])
def config_index():
    """Top page for config uploads.
    """
    cfns = ((c, list_filenames("{}/*.json".format(c))) for c in CONFIG_TYPES)
    flss = [[(fn, flask.url_for("api.get_config", ctype=c, filename=fn))
             for fn in fns] for c, fns in cfns]

    flinks = itertools.chain(*flss)
    ulink = flask.url_for(".config_upload")

    return flask.render_template("config_index.html", flinks=flinks,
                                 ulink=ulink)


@APP.route("/config/upload", methods=["GET", "POST"])
def config_upload():
    """Upload configuration page.
    """
    form = ConfigUploadForm()
    filename = None
    octxs = dict(form=form)

    if form.validate_on_submit():
        cnf_data = form.upload.data
        cnf_type = form.ctype.data

        assert is_valid_config_type(cnf_type)

        filepath = upload_filepath(cnf_data.filename, cnf_type)
        utils.ensure_dir_exists(filepath)

        filename = os.path.basename(filepath)
        cnf_data.save(filepath)

        try:
            parse_config_and_save(filename, cnf_type)
        except (IOError, OSError, ValueError, RuntimeError) as exc:
            flask.flash(u"Failed to convert the data uploaded! "
                        u"Please try again with other valid data files."
                        u"The error was: " + str(exc))
            return flask.render_template("config_upload.html", **octxs)

        flask.flash(u"File was successfully uploaded and processed.")
        return flask.redirect(flask.url_for(".config_index"))

    return flask.render_template("config_upload.html", filename=filename,
                                 **octxs)

# vim:sw=4:ts=4:et:
