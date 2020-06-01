#
# Copyright (C) 2021 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""common globals and utility functions.
"""
import glob
import os.path
import werkzeug.utils

from .. import libs, utils


CTYPE = "fortios"

PREFIX = "/" + CTYPE
API_PREFIX = PREFIX + "/api/v1"


def secure_filename(filename):
    """Just an wrapper for werkzeug.secure_filename
    """
    return werkzeug.utils.secure_filename(filename)


def uploaddir():
    """Fortios' upload dir.
    """
    return utils.uploaddir(libs.FT_FORTI_SHOW_CONFIG)


def host_uploaddir(hostname, secure=True):
    """
    Dir contains config files for the host `hostname`.
    """
    return os.path.join(uploaddir(),
                        secure_filename(hostname) if secure else hostname)


def list_hostnames():
    """
    :return:
        A list of hostnames of fortigate nodes have parsed configuration files
        in <uploaddir>/<hostname>/ on the server
    """
    hdirs = [secure_filename(os.path.basename(d))
             for d in glob.glob(host_uploaddir('*', secure=False))
             if (os.path.isdir(d) and
                 os.path.exists(os.path.join(d, libs.FORTI_CNF_ALL)))]

    return sorted(hdirs)


def list_host_files(hostname, includes=libs.FORTI_FILENAMES):
    """
    List host's data files
    """
    pitr = glob.glob(os.path.join(host_uploaddir(hostname), "*.*"))
    if includes:
        pitr = (p for p in pitr if os.path.basename(p) in includes)

    return sorted(os.path.basename(f) for f in pitr)


def list_hosts_with_data_filenames():
    """
    :return:
        A list of hostnames of fortigate nodes have parsed configuration files
        in <uploaddir>/<hostname>/ on the server, with its config files.
    """
    return [dict(hostname=h, filenames=list_host_files(h))
            for h in list_hostnames()]


def find_firewall_policy_by_addr(hostname, ipa):
    """
    Find firewall policies match given ip address

    :param hostname: a str gives hostname of the fortigate node
    :param ipa: a str gives an ip address

    :return: A list of mappping objects contains results
    :raises: ValueError (could not find/open data file, etc.)
    """
    # Just in case. Maybe I should consider to implement custom converter:
    # https://exploreflask.com/en/latest/views.html#custom-converters
    ipa = secure_filename(ipa)
    hname = secure_filename(hostname)

    rdf = libs.load_firewall_policy_table(hname)

    return libs.search_firewall_policy_by_addr(rdf, ipa)


def upload_forti_show_config(filename, payload):
    """
    Upload and process fortigate's "show *configuration" outputs.

    :param filename:
        a str gives a name of the fortigate's "show *configuration" output
    :param payload: byte data to upload
    """
    content = payload.decode("utf-8")

    ftype = libs.FT_FORTI_SHOW_CONFIG
    fpath = utils.uploaded_filepath(filename, ftype, content=content)
    try:
        utils.ensure_dir_exists(fpath)
        open(fpath, 'wb').write(payload)  # the source

        # process the source and generate JSON and database files.
        (hostname, _cnf) = libs.parse_fortigate_config_and_save_files(fpath)

    except (IOError, OSError, ValueError, RuntimeError) as exc:
        raise RuntimeError(
            "Uploaded data was invalid or something went wrong. "
            "uploaded file: {} exc={!r}".format(filename, exc)
        )

    return dict(hostname=hostname, filenames=list_host_files(hostname))

# vim:sw=4:ts=4:et:
