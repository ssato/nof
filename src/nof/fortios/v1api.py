#
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""REST APIs for fortios app. version 1.x
"""
import flask

from ..globals import FT_FORTI_SHOW_CONFIG
from .. import libs, utils
from . import common


API = flask.Blueprint("forti_api", __name__, url_prefix=common.API_PREFIX)

# url paths :
IDX_PATH = "/"

GET_PATH_0 = "/configs/<string:hostname>/"
GET_PATH_1 = GET_PATH_0 + "<path:filename>"
UP_PATH = "/upload/<path:filename>"

FIND_POLICY_BY_ADDR = "/policies/by_addr/<string:ipa>"


def _get_host_config(hostname, filename):
    """
    Download a parsed and structured JSON file contains fortigate's "show
    *configuration" outputs. FILENAME may be 'all.json', 'metadata.json',
    'firewall_policy_table.data.pickle.gz' and so on (seealso fortios_api's
    sources).

    :param filename: a str gives a name of the fortigate JSON config file
    """
    return flask.send_from_directory(common.host_uploaddir(hostname),
                                     common.secure_filename(filename))


def _upload_show_config(filename):
    """
    Upload and process fortigate's "show *configuration" outputs.

    :param filename:
        a str gives a name of the fortigate's "show *configuration" output
    """
    payload = flask.request.get_data()

    content = payload.decode("utf-8")
    ftype = FT_FORTI_SHOW_CONFIG
    fpath = utils.uploaded_filepath(filename, ftype, content=content)
    try:
        utils.ensure_dir_exists(fpath)

        open(fpath, 'wb').write(payload)  # the source

        # process the source and generate JSON and database files.
        (hostname, cnf) = libs.parse_fortigate_config_and_save_files(fpath)

    except (IOError, OSError, ValueError, RuntimeError) as exc:
        flask.abort(400,
                    dict(code="Invalid data",
                         message="Uploaded data was invalid "
                                 "or something went wrong. "
                                 "uploaded file: {}"
                                 "exc={!r}".format(filename,
                                                   exc)))

    data = dict(hostname=hostname,
                filenames=common.list_host_files(hostname))

    return flask.make_response(flask.jsonify(data), 201)


@API.route("/", methods=["GET"])
def index():
    """
    Get hosts with group config filenames
    """
    res = common.list_hosts_with_data_filenames()
    status = 200 if res else 204  # No content

    return flask.make_response(flask.jsonify(res), status)


@API.route(GET_PATH_0, methods=["GET"])
@API.route(GET_PATH_1, methods=["GET"])
def get_host_config(hostname, filename=libs.FORTI_CNF_ALL):
    """
    Download a JSON data file contains some configs of the node `hostname`.

    :param hostname: a str gives hostname of the fortigate node
    :param filename: a str gives a name of the data file to download
    """
    return _get_host_config(hostname, filename)


@API.route(UP_PATH, methods=["POST"])
def upload_show_config(filename):
    """
    Get or upload a networks JSON data.

    :param filename:
        a str gives a name of the fortigate's "show *configuration" output
    """
    return _upload_show_config(filename)

# vim:sw=4:ts=4:et:
