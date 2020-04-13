#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""nof.fortios.utils - utility routines
"""
import glob
import os.path
import werkzeug.utils

from ..lib import fortios
from ..main import utils
from .globals import CTYPE


CONF_EXT = "json"

CONF_DEFAULTS = """\
all.json
metadata.json
system_interface.json
firewall_address.json
firewall_addrgrp.json
firewall_policy.json
firewall_service_category.json
firewall_service_custom.json
firewall_service_group.json
""".split()


def uploaddir():
    """
    Fortios' upload dir.
    """
    return os.path.join(utils.uploaddir(), CTYPE)


def host_configs_dir(hostname):
    """
    Dir contains config files for the host `hostname`.
    """
    return os.path.join(uploaddir(), hostname)


def list_hostnames():
    """
    :return:
        A list of hostnames of fortigate nodes have parsed configuration files
        in <uploaddir>/<hostname>/ on the server
    """
    hdirs = [werkzeug.utils.secure_filename(os.path.basename(d))
             for d in glob.glob(host_configs_dir('*'))
             if (os.path.isdir(d) and
                 os.path.exists(os.path.join(d, fortios.METADATA_FILENAME)))]

    return sorted(hdirs)


def get_group_config_path(hostname, filename):
    """
    Get the file path of host's group config file.
    """
    hostname = werkzeug.utils.secure_filename(hostname)
    filename = werkzeug.utils.secure_filename(filename)

    return os.path.join(host_configs_dir(hostname), filename)


def list_host_configs(hostname, ext=CONF_EXT, includes=CONF_DEFAULTS):
    """
    List host's (group) config files
    """
    pitr = glob.glob(os.path.join(host_configs_dir(hostname), "*." + ext))
    if includes:
        pitr = (p for p in pitr if os.path.basename(p) in includes)

    return sorted(os.path.basename(f) for f in pitr)


def list_hosts_with_config_filenames(includes=CONF_DEFAULTS):
    """
    :return:
        A list of hostnames of fortigate nodes have parsed configuration files
        in <uploaddir>/<hostname>/ on the server, with its config files.
    """
    return [dict(hostname=h,
                 filenames=list_host_configs(h, includes=includes))
            for h in list_hostnames()]

# vim:sw=4:ts=4:et:
