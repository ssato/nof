#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# flake8: noqa: F401
# pylint: disable=invalid-name,unused-import
"""globals.
"""

PACKAGE = "nof"
AUTHOR = "Satoru SATOH <ssato@redhat.com>"

NOF_DATA_DIR = "/var/lib/nof"

from fortios_xutils import (  # noqa: F401
    NODE_TYPES,
    NODE_ANY, NODE_NET, NODE_HOST, NODE_ROUTER, NODE_SWITCH, NODE_FIREWALL
)

# File types to upload and process
FILE_TYPES = (
    FT_NETWORKS,  # networks (nodes and links) files
    FT_FORTI_SHOW_CONFIG,  # fortios (fortigate) CLI "show *config" outputs
) = (
    "networks",
    "fortios_show_config",
)

# vim:sw=4:ts=4:et:
