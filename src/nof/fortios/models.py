#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=too-few-public-methods
"""Models
"""
import sqlalchemy_utils

from ..db import DB, types as custom_types


FW_ADDR_TYPES = ((u"ipmask", u"IPMask"), (u"iprange", u"IPRange"))

# https://docs.fortinet.com/document/fortigate/6.0.0/handbook/554066/firewall-policies
FW_ACTION_TYPES = ((u"accept", "Accept"), (u"deny", "Deny"),
                   (u"learn", "Learn"), (u"ipsec", "IPSec"))

_VDOM_DEFAULT = "root"


class Firewall(DB.Model):
    """Firewall Node.
    """
    id = DB.Column(DB.Integer, primary_key=True)
    type = DB.Column(DB.String(20), nullable=False)
    name = DB.Column(DB.String(20))
    info = DB.Column(DB.String(120))

    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#one-to-many-relationships
    vdoms = DB.relationship("VDom")
    interfaces = DB.relationship("Interface")
    firewall_sercice_categories = DB.relationship("FirewallServiceCategory")
    firewall_sercice_groups = DB.relationship("FirewallServiceGroup")
    firewall_sercice_customs = DB.relationship("FirewallServiceCustom")
    firewall_addrgrps = DB.relationship("FirewallAddressGrp")
    firewall_addresses = DB.relationship("FirewallAddress")
    firewall_policies = DB.relationship("FirewallPolicy")


class VDom(DB.Model):
    """config vdom

    Example:
        config vdom
            edit root
                ... # TBD.
            next
        end
    """
    id = DB.Column(DB.Integer, primary_key=True)  # ! Edit
    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"))
    edit = DB.Column(DB.String(20), nullable=False)
    name = DB.Column(DB.String(20), nullable=False, default=_VDOM_DEFAULT)


class Interface(DB.Model):
    """config system itnerface

    Example:
        config system interface
            edit "port1"
                set vdom "root"
                set ip 192.168.122.1 255.255.255.0
                set allowaccess ping https ssh snmp
                set vlanforward enable
                set type physical
                set alias "Libvirt_Default_GW"
                set snmp-index 9
            next
        end
    """
    id = DB.Column(DB.Integer, primary_key=True)
    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"))
    edit = DB.Column(DB.String(40), nullable=False,
                     default=FW_ADDR_TYPES[0][0])

    vdom_id = DB.Column(DB.Integer, DB.ForeignKey("vdom.id"),
                        default=_VDOM_DEFAULT)
    vdom = DB.relationship("VDom")

    type = DB.Column(DB.String(10), nullable=False)
    vlanforward = DB.Column(DB.String(10))
    allowaccess = DB.Column(DB.String(40))
    alias = DB.Column(DB.String(20))
    mode = DB.Column(DB.String(10))
    status = DB.Column(DB.String(10))
    snmp_index = DB.Column(DB.Integer, nullable=False)
    ip = DB.Column(custom_types.FortiosSubnetType)


class FirewallServiceCategory(DB.Model):
    """firewall service category

    .. seealso:: https://bit.ly/2wHycuw

    Example:
        config firewall service category
            edit "HTTP Access"
                set comment "http access"
            next
        end
    """
    id = DB.Column(DB.Integer, primary_key=True)
    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"))
    edit = DB.Column(DB.String(40), nullable=False)
    comment = DB.Column(DB.String(50))


class FirewallServiceGroup(DB.Model):
    """firewall service group

    Example:
        config firewall service group
            edit "Web Access"
                set member "DNS" "HTTP" "HTTPS"
                set comment "Web access"
            next
        end
    """
    id = DB.Column(DB.Integer, primary_key=True)
    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"))
    edit = DB.Column(DB.String(40), nullable=False)
    comment = DB.Column(DB.String(50))


class FirewallServiceCustom(DB.Model):
    """firewall service category
    """
    id = DB.Column(DB.Integer, primary_key=True)
    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"))
    edit = DB.Column(DB.String(40), nullable=False)

    category_id = DB.Column(DB.Integer,
                            DB.ForeignKey("firewall_service_category.id"))
    category = DB.relationship("FirewallServiceCategory")

    protocol = DB.Column(DB.String(20))
    protocol_number = DB.Column(DB.Integer)
    comment = DB.Column(DB.String(50))
    session_ttl = DB.Column(DB.Integer)
    udp_portrange = DB.Column(DB.String(50))
    tcp_portrange = DB.Column(DB.String(50))
    explicit_proxy = DB.Column(DB.String(20))
    visibility = DB.Column(DB.String(20))
    icmptype = DB.Column(DB.Boolean())
    icmpcode = DB.Column(DB.Boolean())


class FirewallAddressGrp(DB.Model):
    """Firewall addrgrp
    """
    id = DB.Column(DB.Integer, primary_key=True)
    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"))
    edit = DB.Column(DB.Integer, nullable=False)

    uuid = DB.Column(DB.String(40), nullable=False)
    comment = DB.Column(DB.String(50))  # Optional
    member = DB.relationship("FirewallAddress", lazy=True)


class FirewallAddress(DB.Model):
    """Firewall address{,6}
    """
    id = DB.Column(DB.Integer, primary_key=True)
    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"))
    edit = DB.Column(DB.Integer, nullable=False)

    uuid = DB.Column(DB.String(40), nullable=False)
    type = DB.Column(sqlalchemy_utils.ChoiceType(FW_ADDR_TYPES),
                     nullable=False, default=FW_ADDR_TYPES[0][0])
    comment = DB.Column(DB.String(120))
    associated_interface_id = DB.Column(DB.Integer,
                                        DB.ForeignKey("interface.id"))
    associated_interface = DB.relationship("Interface")

    # iprange:
    start_ip = DB.Column(sqlalchemy_utils.IPAddressType)
    end_ip = DB.Column(sqlalchemy_utils.IPAddressType)

    # ipmask (network or host):
    subnet = DB.Column(custom_types.FortiosSubnetType)


class FirewallPolicy(DB.Model):
    """Firewall Policy
    """
    id = DB.Column(DB.Integer, primary_key=True)
    node_id = DB.Column(DB.ForeignKey("firewall.id"), nullable=False)
    edit = DB.Column(DB.Integer, nullable=False)

    uuid = DB.Column(DB.String(40), nullable=False)  # UUID
    name = DB.Column(DB.String(50))  # Optional
    comments = DB.Column(DB.String(50))  # Optional

    srcintf_id = DB.Column(DB.Integer, DB.ForeignKey("interface.id"))
    srcintf = DB.relationship("Interface")

    dstintf_id = DB.Column(DB.Integer, DB.ForeignKey("interface.id"))
    dstintf = DB.relationship("Interface")

    # firewall addrgrp or firewall address{,6}
    srcaddr_group_id = DB.Column(DB.Integer,
                                 DB.ForeignKey("firewall_addresse_grp.id"))
    srcaddr_group = DB.relationship("FirewallAddressGrp")
    srcaddr_id = DB.Column(DB.Integer, DB.ForeignKey("firewall_addresse.id"))
    srcaddr = DB.relationship("FirewallAddress")

    dstaddr_group_id = DB.Column(DB.Integer,
                                 DB.ForeignKey("firewall_addresse_grp.id"))
    dstaddr_group = DB.relationship("FirewallAddressGrp")
    dstaddr_id = DB.Column(DB.Integer, DB.ForeignKey("firewall_addresse.id"))
    dstaddr = DB.relationship("FirewallAddress")

    # firewwall service group or firewall_policy service custom
    serivce_group_id = DB.Column(DB.Integer,
                                 DB.ForeignKey("firewall_sercice_groups.id"))
    serivce_group = DB.relationship("FirewallServiceGroup")
    serivce_custom_id = DB.Column(DB.Integer,
                                  DB.ForeignKey("firewall_sercice_custom.id"))
    serivce_custom = DB.relationship("FirewallServiceCustom")

    logtraffic = DB.Column(DB.String(10))
    schedule = DB.Column(DB.String(10), default="always")
    status = DB.Column(DB.String(10))

    action = DB.Column(sqlalchemy_utils.ChoiceType(FW_ACTION_TYPES),
                       default=FW_ACTION_TYPES[0][0])

# vim:sw=4:ts=4:et:
