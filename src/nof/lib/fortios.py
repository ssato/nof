#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
r"""Parse fortios configuration

.. versionadded:: 0.1.0

   - initial checkin
"""
from __future__ import absolute_import

import collections
import itertools
import os.path
import re

import anyconfig

from .utils import ensure_dir_exists


CONFIG_GROUPS = (CONFIG_GROUP_FIREWALL,  # default
                 CONFIG_GROUP_ROUTER) = ("firewall", "router")
CNF_GRPS = dict(firewall=("vdom", "system interface",
                          "firewall service category",
                          "firewall service group",
                          "firewall service custom",
                          "firewall addrgrp",
                          "firewall address",
                          "firewall policy"),
                system="system *")

FIREWALL_COLS = (dict(key="name", width="5%"),
                 dict(key="uuid", width="5%", hide=True),
                 dict(key="srcaddr", width="10%"),
                 dict(key="srcintf", width="5%"),
                 dict(key="dstaddr", width="10%"),
                 dict(key="dstintf", width="5%"),
                 dict(key="service", width="10%"),
                 dict(key="status", width="3%"),
                 dict(key="action", width="3%"),
                 dict(key="logtraffic", width="3%"),
                 dict(key="comments", width="5%"),
                 dict(key="schedule", width="5%"))

EMPTY_RE = re.compile(r"^\s+$")
COMMENT_RE = re.compile(r"^#(.*)$")

WORD_RE_S = r'(?:([^" \t\n\r\f\v]+)|"([^"]+)")'

# Examples:
# - 'config firewall address'
# - '       config ftgd-wf'
# - '            config filters'
CONFIG_START_RE = re.compile(r"^(\s*)"
                             r"config\s+"
                             r"(.+)$")
# Examples:
# - '     edit "fortinet"'
# - '            edit 1'
EDIT_START_RE = re.compile(r"^(\s+)"
                           r"edit\s+"
                           + WORD_RE_S +
                           r"$")
SET_OR_UNSET_LINE_RE = re.compile(r"^\s+"
                                  r"(set|unset)\s+"
                                  r"(\S+)\s*"
                                  r"(.+)*$")
SET_VALUE_RE = re.compile(WORD_RE_S + r"\s*")

(ST_IN_CONFIG, ST_IN_EDIT, ST_OTHER) = list(range(3))


def process_config_or_edit_line(matched):
    """
    :param matched: :class:`re.Match` object holding the config line info

    :raises: ValueError
    :return: A tuple of (indent_str, config_name_str)
    """
    matches = matched.groups()
    if len(matches) < 2:
        msg = "line: {}, matches: {}".format(matched.string,
                                             ", ".join(matches))
        raise ValueError(msg)

    if len(matches) > 2:  # edit
        vals = [m for m in matches[1:] if m][0]
    else:
        vals = matches[1]

    return (matches[0], vals)


def process_set_or_unset_line(matched):
    """
    :param matched: :class:`re.Match` object holding the '*set' line info

    :raises: ValueError
    :return: A tuple of (name, type, *args)
    """
    matches = [m for m in matched.groups() if m is not None]
    if len(matches) < 2:
        msg = "line: {}, matches: {}".format(matched.string,
                                             ", ".join(matches))
        raise ValueError(msg)

    if len(matches) == 2:  # ex. unset ssd-trim-weekday
        return dict(type=matches[0], name=matches[1])

    vss = SET_VALUE_RE.findall(matches[2])
    values = [m for m in itertools.chain.from_iterable(vss) if m]

    return dict(type=matches[0], name=matches[1], values=values)


(NT_CONFIG, NT_EDIT) = ("config", "edit")


def make_end_re(indent, _type=None):
    """
    Make a regex object to match for 'config' or 'edit' section ends
    """
    end = "next$" if _type == NT_EDIT else "end$"
    return re.compile(r"^" + indent + end)


def make_Node(matched, _type=None):
    """
    :param matched: :class:`re.Match` object holding the config line info
    :param _type: Node type

    :return: A collections.namedtuple object has a config or edit info
    """
    if _type is None:
        _type = NT_CONFIG

    (indent, name) = process_config_or_edit_line(matched)
    end_re = make_end_re(indent, _type)

    Node = collections.namedtuple(_type.title(),
                                  ("name", "type", "end_re", "children"))
    return Node(name=name, type=_type, end_re=end_re, children=[])


CNF_NAME = CNF_TYPE = "config"
EDIT_NAME = EDIT_TYPE = "edit"


def _process_vals(vals):
    """
    :param vals: None or a single value in a list of a list

    >>> _process_vals(None)
    None
    >>> _process_vals([])
    []
    >>> _process_vals([0])
    0
    >>> _process_vals(["0", "1"])
    ['1', '2']
    """
    if vals is None or not vals:
        return vals

    if len(vals) == 1:  # single value in a list
        return vals[0]

    return vals


def Node_to_dict(node, verbose=False):
    """Convert a Node namedtuple object to a dict.

    :param verbose: return verbose dict if True
    """
    if verbose:
        return dict(name=node.name, type=node.type, children=node.children)

    ccnfs = [c for c in node.children if CNF_NAME in c]  # config in children
    cedits = [e for e in node.children if EDIT_NAME in e]  # edit in children

    # set or unset in children
    cmaps = dict((x["name"], _process_vals(x.get("values", None)))
                 for x in node.children if x.get("type") in ("set", "unset"))
    if ccnfs:
        cmaps["configs"] = ccnfs

    if cedits:
        cmaps["edits"] = cedits

    if node.type == EDIT_TYPE:
        return dict(edit=node.name, **cmaps)

    return dict(config=node.name, **cmaps)


def _process_comment(content):
    """
    Parse comment content, make a mapping objects and return it.

    :param content: A str represents a comment
    :return: A mapping object made by parsing a comment
    """
    return dict(kv.split('=') for kv in content.split(':'))


def parse_show_config_itr(lines, verbose=False):
    """
    Parse 'config xxxxx xxxx' .. 'end'.

    :param lines: An iterator yields each lines in the configuration outputs
    :param verbose: return verbose result if True
    """
    state = ST_OTHER
    configs = []  # stack holds nested config objects

    # A dict holds comments; There are not so many comments.
    comments = dict(comments=[])

    for line in lines:
        if EMPTY_RE.match(line):
            continue

        matched = COMMENT_RE.match(line)
        if matched:
            content = matched.groups()[0].strip()
            comments["comments"].append(content)
            try:
                comments.update(_process_comment(content))
            except ValueError:
                continue  # content does not contain structured data.

        elif state == ST_OTHER:
            matched = CONFIG_START_RE.match(line)
            if matched:
                state = ST_IN_CONFIG

                config = make_Node(matched)
                configs.append(config)  # push config

        elif state == ST_IN_CONFIG:
            matched = EDIT_START_RE.match(line)
            if matched:
                state = ST_IN_EDIT

                edit = make_Node(matched, _type=NT_EDIT)
                configs.append(edit)  # push edit
                continue

            assert configs[-1].type == NT_CONFIG, configs[-1]
            matched = configs[-1].end_re.match(line)
            if matched:
                config = Node_to_dict(configs.pop(), verbose)

                if not configs:  # It's a top level object.
                    state = ST_OTHER
                    yield config
                else:
                    state = ST_IN_EDIT
                    configs[-1].children.append(config)

                continue

            matched = SET_OR_UNSET_LINE_RE.match(line)
            if matched:
                set_val = process_set_or_unset_line(matched)
                configs[-1].children.append(set_val)

        elif state == ST_IN_EDIT:
            assert configs[-1].type == NT_EDIT, configs[-1]
            matched = configs[-1].end_re.match(line)
            if matched:
                state = ST_IN_CONFIG

                edit = Node_to_dict(configs.pop(), verbose)
                configs[-1].children.append(edit)
                continue

            matched = SET_OR_UNSET_LINE_RE.match(line)
            if matched:
                set_val = process_set_or_unset_line(matched)
                configs[-1].children.append(set_val)
                continue

            matched = CONFIG_START_RE.match(line)
            if matched:
                state = ST_IN_CONFIG

                config = make_Node(matched)
                configs.append(config)  # push config

    if comments["comments"]:
        if verbose:
            comments["type"] = comments["name"] = "comment"  # TBD
        yield comments


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


def parse_show_config(filepath, verbose=False):
    """
    Parse 'show full-configuration output and returns a list of parsed configs.

    :param filepath:
        a str or :class:`pathlib.Path` object represents file path contains
        'show full-configuration` or any other 'show ...' outputs
    :param verbose: return verbose result if True

    :return:
        A list of configs (mapping objects) or [] (no data or something went
        wrong)
    :raises: IOError, OSError
    """
    for enc in ("utf-8", "shift-jis"):
        try:
            lines = open(filepath, encoding=enc)
            return list(parse_show_config_itr(lines, verbose))
        except UnicodeDecodeError:
            pass  # Try the next encoding...

    return []


def group_config_path(filepath, group):
    """
    Compute the path of the group config file.

    :param filepath: (JSON) file path contains parsed results
    """
    return os.path.join(os.path.dirname(filepath), group + ".json")


def parse_show_config_and_dump(inpath, outpath, verbose=False):
    """
    Similiar to the above :func:`parse_show_config` but save results as JSON
    file (path: `outpath`).

    :param inpath:
        a str or :class:`pathlib.Path` object represents file path contains
        'show full-configuration` or any other 'show ...' outputs
    :param outpath: (JSON) file path to save parsed results
    :param verbose: save verbose result if True

    :return: A mapping object contains parsed results
    :raises: IOError, OSError
    """
    configs = parse_show_config(inpath, verbose)
    data = dict(configs=configs)

    ensure_dir_exists(outpath)
    anyconfig.dump(data, outpath)

    if verbose:
        return data

    for grp in CNF_GRPS.keys():
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
    if group not in CONFIG_GROUPS:
        raise ValueError("Given {} is not valid group. Try other one from"
                         " {}".format(group, ", ".join(CONFIG_GROUPS)))
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
