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
import re


EMPTY_RE = re.compile(r"^\s+$")
COMMENT_RE = re.compile(r"^#(.*)$")

# Examples:
# - 'config firewall address'
# - '       config ftgd-wf'
# - '            config filters'
CONFIG_START_RE = re.compile(r"^(\s*)"
                             r"config\s+"
                             r'(?:([^"\s]+)|"([^"\s]+)")' r"(?# word )"
                             r"(?:\s+"
                             r'(?:([^"\s]+)|"([^"\s]+)")'
                             r")*$")
CONFIG_END_RE = re.compile(r"^end$")

# Examples:
# - '     edit "fortinet"'
# - '            edit 1'
EDIT_START_RE = re.compile(r"^(\s+)"
                           r"edit\s+"
                           r'(?:([^"\s]+)|"([^"\s]+)")'
                           r"$")
EDIT_END_RE = re.compile(r"next$")
SET_OR_UNSET_LINE_RE = re.compile(r"^\s+"
                                  r"(set|unset)\s+"
                                  r'(?:([^"\s]+)|"([^"\s]+)")' r"(?# key )"
                                  r"(?:\s+"
                                  r"(.+)"
                                  r")?$")
SET_VALUE_RE = re.compile(r'(?:([^"\s]+)|"([^"\s]+)")\s*')

(ST_IN_CONFIG, ST_IN_EDIT, ST_OTHER) = list(range(3))


def is_not_empty_nor_white_spaces(astr):
    """
    True if given string is not empty or does not consists of white spaces.
    """
    return astr and astr.strip()


def list_matches(matches, cond=None):
    """
    :param matches: A list of matched strings or None
    :return: A list of matched strings only
    """
    if cond is None:
        cond = is_not_empty_nor_white_spaces

    return [m for m in matches if cond(m)]


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

    return (matches[0],
            ' '.join(list_matches(matches[1:])))  # TBD: What to return?


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


def make_Node(name, id_gen, _type=None):
    """Make a collections.namedtuple object represents a config node.
    """
    if _type is None:
        _type = NT_CONFIG

    Node = collections.namedtuple("Config", ("name", "id", "type",
                                             "children"))
    return Node(name=name, id=id_gen(), type=_type, children=[])


def Node_to_dict(node):
    """Convert a Node namedtuple object to a dict.
    """
    return dict(name=node.name, _id=node.id, type=node.type,
                children=node.children)


def parse_show_config_itr(lines):
    """
    Parse 'config xxxxx xxxx' .. 'end'.

    :param lines: A list of lines in the configuration outputs
    :param indent: indent string (leading white spaces)
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

                (indent, name) = process_config_or_edit_line(matched)
                config = make_Node(name, id_gen, _type=NT_CONFIG)
                configs.append(config)  # push config

        elif state == ST_IN_CONFIG:
            if indent:
                # strip leading white spaces to try the next match.
                line = re.sub(r"^" + indent, '', line)

            matched = EDIT_START_RE.match(line)
            if matched:
                state = ST_IN_EDIT

                (edit_indent, name) = process_config_or_edit_line(matched)
                edit = make_Node(name, id_gen, _type=NT_EDIT)
                configs.append(edit)  # push edit

            matched = CONFIG_END_RE.match(line)
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
            if edit_indent:
                line = re.sub(r"^" + indent + edit_indent, '', line)

            matched = EDIT_END_RE.match(line)
            if matched:
                edit = Node_to_dict(configs.pop())
                configs[-1].children.append(edit)

                state = ST_IN_CONFIG
                continue

            matched = SET_OR_UNSET_LINE_RE.match(line)
            if matched:
                set_val = process_set_or_unset_line(matched)
                configs[-1].children.append(set_val)


def parse_show_config(filepath):
    """Parse configuration output and returns a list of firewwall policies.
    """
    try:
        lines = open(filepath).readlines()
    except UnicodeDecodeError:
        lines = open(filepath, encoding="shift-jis").readlines()

    return list(parse_show_config_itr(lines))

# vim:sw=4:ts=4:et:
