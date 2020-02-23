#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
# pylint: disable=invalid-name
"""globals.
"""

PACKAGE = "nof"
AUTHOR = "Satoru SATOH <ssato@redhat.com>"
VERSION = "0.1.0"


NODE_TYPES = (NODE_ANY, NODE_NET, NODE_ROUTER, NODE_FIREWALL, NODE_SWITCH,
              NODE_HOST) \
           = ("any", "network", "firewall", "router", "switch", "host")

# .. seealso:: lib.configparsers
CONFIG_TYPES = (CONFIG_FORTIOS, ) \
             = ("fortios", )

# vim:sw=4:ts=4:et:
