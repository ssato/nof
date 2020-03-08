#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>
# SPDX-License-Identifier: MIT
#
"""Custom types

.. seealso:: https://docs.sqlalchemy.org/en/13/core/custom_types.html
"""
import ipaddress
import re

import sqlalchemy.types


FORTIOS_SUBNET_RE = re.compile(r"^(?:\d+\.){3}\d+ (?:\d+\.){3}\d+$")


def to_ip_iface(value):
    """
    Convert a fortios 'subnet' string in config firewall section to an
    ipaddress.IPv{4,6}Interface object.

    >>> s = '192.168.1.12 255.255.255.0'
    >>> to_ip_iface(s)
    IPv4Interface('192.168.1.12/24')
    >>> s = '10.1.0.0 255.255.0.0'
    >>> to_fortios_subnet(s)
    IPv4Interface('10.1.0.0/16')
    """
    if FORTIOS_SUBNET_RE.match(value) is None:
        raise ValueError("Given str does not look subnet: {!s}".format(value))

    return ipaddress.ip_interface(value.replace(' ', '/'))


def to_fortios_subnet(value):
    """
    Convert an ipaddress.IPv{4,6}Interface object to a fortios 'subnet' string
    in config firewall section.

    >>> val = ipaddress.ip_interface("192.168.1.12/24")
    >>> to_fortios_subnet(val_v)
    '192.168.1.12 255.255.255.0'
    >>> val = ipaddress.ip_interface("10.1.0.0/16")
    >>> to_fortios_subnet(val)
    '10.1.0.0 255.255.0.0'
    """
    return "{!s} {!s}".format(value.ip, value.netmask)


class FortiosSubnetType(sqlalchemy.types.TypeDecorator):
    """
    IP Address or Network Address type backed with ipaddress.ip_interface to
    store/convert fortigate 'subnet' string in config firewall section.

    .. seealso:: https://bit.ly/2VQ55j7
    """
    impl = sqlalchemy.types.Unicode(80)

    def process_bind_param(self, value, dialect):
        """Store `value` as unicode string or None.
        """
        return value if value else None

    def process_result_value(self, value, dialect):
        """Convert `value` using ipaddress.ip_network
        """
        return to_ip_iface(value) if value else None

# vim:sw=4:ts=4:et:
