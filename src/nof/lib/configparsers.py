#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
r"""Parse collection

.. versionadded:: 0.1.0

   - initial checkin
"""
from __future__ import absolute_import

from . import fortios


# .. seealso:: ..globals.CONFIG_TYPES
PARSERS = dict(fortios=fortios.parse_show_config)

# vim:sw=4:ts=4:et:
