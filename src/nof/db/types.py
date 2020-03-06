#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>
# SPDX-License-Identifier: MIT
#
"""Custom types

.. seealso:: https://docs.sqlalchemy.org/en/13/core/custom_types.html
"""
import ipaddress
import sqlalchemy.types


class IPNetworkType(sqlalchemy.types.TypeDecorator):
    """
    IP Network Address type backed with ipaddress.ip_network
    """
    impl = sqlalchemy.types.Unicode(80)

    def process_bind_param(self, value, dialect):
        """Store `value` as unicode string or None.
        """
        return value if value else None

    def process_result_value(self, value, dialect):
        """Convert `value` using ipaddress.ip_network
        """
        return ipaddress.ip_network(value) if value else None

# vim:sw=4:ts=4:et:
