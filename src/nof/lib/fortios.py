#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
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


CONFIG_GROUPS = (CONFIG_GROUP_FIREWALL,  # default
                 CONFIG_GROUP_ROUTER) = ("firewall", "router")
FIREWALL_KEYS = ("action", "comments", "dstaddr", "dstintf",
                 "logtraffic", "name", "schedule", "service",
                 "srcaddr", "srcintf", "status", "uuid")

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


def make_Node(matched, id_gen, _type=None):
    """
    :param matched: :class:`re.Match` object holding the config line info
    :param id_gen: Any callable to generate unique ID of this node object
    :param _type: Node type

    :return: A collections.namedtuple object has a config or edit info
    """
    if _type is None:
        _type = NT_CONFIG

    (indent, name) = process_config_or_edit_line(matched)
    end_re = make_end_re(indent, _type)

    Node = collections.namedtuple(_type.title(),
                                  ("name", "id", "type", "end_re", "children"))
    return Node(name=name, id=id_gen(), type=_type, end_re=end_re, children=[])


def Node_to_dict(node):
    """Convert a Node namedtuple object to a dict.
    """
    return dict(name=node.name, _id=node.id, type=node.type,
                children=node.children)


def parse_show_config_itr(lines):
    """
    Parse 'config xxxxx xxxx' .. 'end'.

    :param lines: An iterator yields each lines in the configuration outputs
    """
    counter = itertools.count()
    state = ST_OTHER
    configs = []  # stack holds nested config objects

    def id_gen():
        """ID generator"""
        return next(counter)

    for line in lines:
        if EMPTY_RE.match(line):
            continue

        matched = COMMENT_RE.match(line)
        if matched:
            yield dict(type="comment", content=matched.groups()[0])  # TBD

        if state == ST_OTHER:
            matched = CONFIG_START_RE.match(line)
            if matched:
                state = ST_IN_CONFIG

                config = make_Node(matched, id_gen)
                configs.append(config)  # push config

        elif state == ST_IN_CONFIG:
            matched = EDIT_START_RE.match(line)
            if matched:
                state = ST_IN_EDIT

                edit = make_Node(matched, id_gen, _type=NT_EDIT)
                configs.append(edit)  # push edit
                continue

            assert configs[-1].type == NT_CONFIG, configs[-1]
            matched = configs[-1].end_re.match(line)
            if matched:
                config = Node_to_dict(configs.pop())  # pop config

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

                edit = Node_to_dict(configs.pop())
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

                config = make_Node(matched, id_gen)
                configs.append(config)  # push config


def _val_or_vals(obj):
    """
    :return: An item or a list of items
    """
    return obj[0] if len(obj) == 1 else obj


def _make_edit_0(edit):
    """
    Make a mapping object contains edit configurations.

    :param edit:
        A mapping object contains edit configurations loaded from parsed
        configs, e.g. edit configurations of '1' in 'firewall policy'.
    :return: A mapping object sorted and organized better than `edit`
    """
    unsets = [c["name"] for c in edit.get("children", [])
              if c["type"] == "unset"]
    sets = [(c["name"], _val_or_vals(c["values"]))
            for c in edit.get("children", []) if c["type"] == "set"]

    if unsets:
        return dict(sets + [("unset", unsets)])

    return dict(sets)


def _make_config_0(cnf, prefix):
    """
    Make a mapping object contains configurations by category.

    :param cnf:
        A mapping object contains configurations of a category loaded from
        parsed configs, e.g. configurations of 'firewall policy'
    :return: A mapping object sorted, modified and organized better than `cnf`
    """
    name = re.sub(prefix, '', cnf["name"])
    configs = dict((e["name"], _make_edit_0(e))
                   for e in cnf.get("children", []))

    return (name, configs)


def make_group_configs(cnfs, group=None):
    """
    :param cnfs: {"configs": [<a mapping object holds configurations>]}
    :param group: Group name of configurations

    :return: Re-structured mapping object having sub group configurations
    :raises: IOError, OSError, TypeError, AttributeError
    """
    # pattern ex. "firewall policy"
    prefix = (group or CONFIG_GROUPS[0]) + ' '
    fwcs = [x for x in cnfs.get("configs", [])
            if x["type"] == "config" and x["name"].startswith(prefix)]

    ret = dict(_make_config_0(c, prefix) for c in fwcs)

    return ret


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
            lines = open(filepath, encoding=enc)
            return list(parse_show_config_itr(lines))
        except UnicodeDecodeError:
            pass  # Try the next encoding...

    return []


def group_config_path(filepath, group):
    """
    Compute the path of the group config file.

    :param filepath: (JSON) file path contains parsed results
    """
    (outbn, outext) = os.path.splitext(filepath)

    return "{}_{}{}".format(outbn, group, outext)


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
    configs = parse_show_config(inpath)
    data = dict(configs=configs)

    outdir = os.path.dirname(outpath)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    anyconfig.dump(data, outpath)

    for grp in CONFIG_GROUPS:
        g_outpath = group_config_path(outpath, grp)
        g_cnfs = make_group_configs(data, grp)
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
