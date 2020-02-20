#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
r"""Parse fortios configuration

.. versionadded:: 0.1.0

   - initial checkin
"""
from __future__ import absolute_import

import re


_COMMENT_RE = re.compile(r"^(?:\s+)?#")
_SECTION_END_RE = re.compile(r"^end$")
_ITEM_END_RE = re.compile(r"^\s+next$")

_FIREWALL_POLICY_SECT_START_RE = re.compile(r"^config firewall policy$")
_FIREWALL_POLICY_SECT_END_RE = _SECTION_END_RE
_FIREWALL_POLICY_ITEM_START_RE = re.compile(r"^\s+edit (\d+)$")
_FIREWALL_POLICY_ITEM_LINE_RE = re.compile(r"\s+set ([a-z0-9-]+) (.+)$")
_FIREWALL_POLICY_ITEM_END_RE = _ITEM_END_RE


def parse_firewall_policy_itr(lines):
    """
    :param lines:
        A list of configuration strings, ['config firewall policy', '    edit
        10', '        set name ...', ..., 'end']
    """
    in_sect = False
    in_item = False
    item = dict()

    for line in lines:
        if _COMMENT_RE.match(line):  # skip comments
            continue

        if _FIREWALL_POLICY_SECT_START_RE.match(line):
            in_sect = True
            continue

        if in_sect:
            if _FIREWALL_POLICY_SECT_END_RE.match(line):
                return  # 'config firewall policy' section was end.

            if _FIREWALL_POLICY_ITEM_START_RE.match(line):
                in_item = True
                continue

            if in_item:
                if _FIREWALL_POLICY_ITEM_END_RE.match(line):
                    in_item = False
                    yield item
                    item = dict()
                else:
                    matched = _FIREWALL_POLICY_ITEM_LINE_RE.match(line)
                    if matched:
                        (key, val) = matched.groups()
                        item[key] = val


def parse_firewall_policy(filepath):
    """Parse configuration output and returns a list of firewwall policies.
    """
    try:
        lines = open(filepath).readlines()
    except UnicodeDecodeError:
        lines = open(filepath, encoding="shift-jis").readlines()

    return list(parse_firewall_policy_itr(lines))

# vim:sw=4:ts=4:et:
