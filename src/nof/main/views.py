#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
"""Views.
"""
import os.path

import flask

from .forms import (
    UploadForm, NetworkFinderForm, PathFinderForm, ConfigUploadForm
)
from .globals import APP
from .utils import (
    graph_path, generate_node_link_data_from_graph_data, list_graph_filenames,
    find_networks_from_graph, find_paths_from_graph,
    upload_filepath, parse_config_and_dump_json_file,
    FORTIOS_FWP_PREFIX
)
from ..globals import NODE_ANY


SUMMARIES = dict(index=u"NOF",
                 upload=u"Upload Network Graph data",
                 finder=u"Find Network Objects")


@APP.route("/", methods=["GET"])
def index():
    """Top page.
    """
    filenames = list_graph_filenames()
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
        filepath = graph_path(yml_data.filename)
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
    fns = list_graph_filenames(pattern="{}*.json".format(FORTIOS_FWP_PREFIX))
    flinks = [(fn, flask.url_for("api.get_config", filename=fn)) for fn in fns]

    return flask.render_template("config_index.html", flinks=flinks)


@APP.route("/config/upload", methods=["GET", "POST"])
def upload_config():
    """Upload configuration page.
    """
    form = ConfigUploadForm()
    filename = None
    octxs = dict(form=form)

    if form.validate_on_submit():
        cnf_data = form.upload.data
        cnf_type = form.ctype

        filepath = upload_filepath(cnf_data.filename)
        filename = os.path.basename(filepath)
        cnf_data.save(filepath)

        try:
            parse_config_and_dump_json_file(filename, ctype=cnf_type)
        except (IOError, OSError, ValueError, RuntimeError):
            flask.flash(u"Failed to convert the data uploaded! "
                        u"Please try again with other valid data files.")
            return flask.render_template("upload.html", **octxs)

        flask.flash(u"File was successfully uploaded and processed.")
        return flask.redirect(flask.url_for(".config_index"))

    return flask.render_template("upload.html", filename=filename, **octxs)

# vim:sw=4:ts=4:et:
