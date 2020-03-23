#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
r"""Parse fortios configuration

.. versionadded:: 0.1.0

   - initial checkin
"""
from __future__ import absolute_import

import os.path

import anyconfig

from .utils import ensure_dir_exists


CNF_GRPS = dict(firewall=("vdom", "system interface",
                          "firewall service category",
                          "firewall service group",
                          "firewall service custom",
                          "firewall addrgrp",
                          "firewall address",
                          "firewall policy"),
                log="log *",
                report="report *",
                router="router *",
                system="system *",
                user="user *")

def make_group_configs(cnfs, group=None):
    """
    :param cnfs: {"configs": [<a mapping object holds configurations>]}
    :param group: Group name of configurations

    :return: Re-structured mapping object having sub group configurations
    :raises: IOError, OSError, TypeError, AttributeError
    """
    fwcs = dict()
    cnf_names = CNF_GRPS.get(group, [])  # (name_0, ..) or glob pattern

    if cnf_names:
        fwcs = dict((c["config"].lower(), c) for c in cnfs.get("configs", [])
                    if (c.get("config", '').startswith(cnf_names.replace('*',
                                                                         ''))
                        if '*' in cnf_names else c.get("config") in cnf_names))
    return fwcs


def parse_show_config(filepath):
    """
    Parse 'show full-configuration output and returns a list of parsed configs.

    :param filepath:
        a str or :class:`pathlib.Path` object represents file path contains
        'show full-configuration` or any other 'show ...' outputs

    :return:
        A list of configs (mapping objects) or [] (no data or something went
        wrong)
    :raises: IOError, OSError
    """
    for enc in ("utf-8", "shift-jis"):
        try:
            with open(filepath, encoding=enc) as inp:
                return anyconfig.load(inp, ac_parser="fortios")
        except UnicodeDecodeError:
            pass  # Try the next encoding...

    return None


def group_config_path(filepath, group):
    """
    Compute the path of the group config file.

    :param filepath: (JSON) file path contains parsed results
    """
    return os.path.join(os.path.dirname(filepath), group + ".json")


def parse_show_config_and_dump(inpath, outpath):
    """
    Similiar to the above :func:`parse_show_config` but save results as JSON
    file (path: `outpath`).

    :param inpath:
        a str or :class:`pathlib.Path` object represents file path contains
        'show full-configuration` or any other 'show ...' outputs
    :param outpath: (JSON) file path to save parsed results

    :return: A mapping object contains parsed results
    :raises: IOError, OSError
    """
    data = parse_show_config(inpath)

    ensure_dir_exists(outpath)
    anyconfig.dump(data, outpath)

    for grp in CNF_GRPS:
        g_outpath = group_config_path(outpath, grp)
        ensure_dir_exists(g_outpath)

        g_cnfs = make_group_configs(data, grp)
        if g_cnfs:
            anyconfig.dump(g_cnfs, g_outpath)

    return data


def assert_group(group):
    """
    :param group: Group name of configurations
    :raises: ValueError
    """
    if group not in CNF_GRPS:
        raise ValueError("Given {} is not valid group. Try other one from"
                         " {}".format(group, ", ".join(CNF_GRPS.keys())))
    return True


def load_configs(filepath, group=None):
    """
    :param filepath: (JSON) file path contains parsed results
    :raises: IOError, OSError, TypeError, AttributeError, ValueError
    """
    if group is not None:
        assert_group(group)
        filepath = group_config_path(filepath, group)

    return anyconfig.load(filepath)

# vim:sw=4:ts=4:et:
