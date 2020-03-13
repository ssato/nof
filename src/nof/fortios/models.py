#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=too-few-public-methods
"""Models

ref. https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
"""
import sqlalchemy.ext.declarative.base
import sqlalchemy_utils

from ..db import DB, types as custom_types


FW_ADDR_TYPES = ((u"ipmask", u"IPMask"), (u"iprange", u"IPRange"))

# https://docs.fortinet.com/document/fortigate/6.0.0/handbook/554066/firewall-policies
FW_ACTION_TYPES = ((u"accept", "Accept"), (u"deny", "Deny"),
                   (u"learn", "Learn"), (u"ipsec", "IPSec"))

# pylint: disable=line-too-long
# https://help.fortinet.com/fos60hlp/60/Content/FortiOS/fortigate-networking/Interfaces/Administrative%20access.htm
# pylint: enable=line-too-long
FW_IFACE_ACCESS_TYPES = (("ping", "PING access"), ("https", "HTTPS access"),
                         ("http", "HTTP access"), ("ssh", "SSH access"),
                         ("snmp", "SNMP access"), ("telnet", "TELNET access"),
                         ("fgfm", "FortiManager access"),
                         ("radius-acct", "RADIUS accounting access"),
                         ("probe-response", "Probe access"),
                         ("capwap", "CAPWAP access"),
                         ("ftm", "FortiToken Mobile Push access"))

_VDOM_DEFAULT = "root"

BASE = sqlalchemy.ext.declarative.declarative_base()


class Firewall(DB.Model):
    """Firewall Node.
    """
    id = DB.Column(DB.Integer, primary_key=True)
    type = DB.Column(DB.String(20), nullable=False, default="fortios")
    name = DB.Column(DB.String(20))
    info = DB.Column(DB.String(120))

    # one-to-many relationships
    ref = "firewall"
    vdoms = DB.relationship("VDom", backref=ref)
    interfaces = DB.relationship("Interface", backref=ref)
    firewall_service_categories = DB.relationship("FirewallServiceCategory",
                                                  backref=ref)
    firewall_service_groups = DB.relationship("FirewallServiceGroup",
                                              backref=ref)
    firewall_service_customs = DB.relationship("FirewallServiceCustom",
                                               backref=ref)
    firewall_addrgrps = DB.relationship("FirewallAddressGrp", backref=ref)
    firewall_addresses = DB.relationship("FirewallAddress", backref=ref)
    firewall_policies = DB.relationship("FirewallPolicy", backref=ref)


class VDom(DB.Model):
    """config vdom

    Example:
        config vdom
            edit root
                ... # TBD.
            next
        end
    """
    __tablename__ = "vdom"

    id = DB.Column(DB.Integer, primary_key=True)  # ! Edit
    edit = DB.Column(DB.String(20), nullable=False, default="1")
    name = DB.Column(DB.String(20), nullable=False, default=_VDOM_DEFAULT)

    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"),
                        nullable=False)


class AllowedAccessTypes(DB.Model):
    """
    "system interface".allowaccess
    """
    id = DB.Column(DB.Integer, primary_key=True)
    type = DB.Column(sqlalchemy_utils.ChoiceType(FW_IFACE_ACCESS_TYPES),
                     nullable=False, default=FW_IFACE_ACCESS_TYPES[0][0])


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
    __tablename__ = "interface"

    id = DB.Column(DB.Integer, primary_key=True)
    edit = DB.Column(DB.String(40), nullable=False,
                     default=FW_ADDR_TYPES[0][0])

    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"),
                        nullable=False)

    vdom_id = DB.Column(DB.Integer, DB.ForeignKey("vdom.id"))
    vdom = DB.relationship("VDom", backref=(DB.backref("interfaces")))

    type = DB.Column(DB.String(10), nullable=False)
    vlanforward = DB.Column(DB.String(10))

    # .. todo::
    # allowaccess = DB.relationship("AllowedAccessTypes")
    allowaccess = DB.Column(DB.String(100))

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
    edit = DB.Column(DB.String(40), nullable=False)
    comment = DB.Column(DB.String(50))

    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"),
                        nullable=False)


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
    edit = DB.Column(DB.String(40), nullable=False)
    comment = DB.Column(DB.String(50))

    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"),
                        nullable=False)


class FirewallServiceCustom(DB.Model):
    """firewall service custom
    """
    id = DB.Column(DB.Integer, primary_key=True)
    edit = DB.Column(DB.String(40), nullable=False)

    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"),
                        nullable=False)

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


# many-to-many
FAG_FAS = DB.Table(
    "fag_fas", DB.metadata,
    DB.Column("address_id", DB.Integer, DB.ForeignKey("firewall_address.id")),
    DB.Column("group_id", DB.Integer, DB.ForeignKey("firewall_address_grp.id"))
)


class FirewallAddressGrp(DB.Model):
    """Firewall addrgrp
    """
    id = DB.Column(DB.Integer, primary_key=True)
    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"))
    edit = DB.Column(DB.Integer, nullable=False)

    uuid = DB.Column(DB.String(40), nullable=False)
    comment = DB.Column(DB.String(50))  # Optional
    member = DB.relationship("FirewallAddress", secondary=FAG_FAS,
                             lazy="subquery",
                             backref=DB.backref("firewall_address_grps"))


class FirewallAddress(DB.Model):
    """Firewall address{,6}
    """
    __tablename__ = "firewall_address"
    id = DB.Column(DB.Integer, primary_key=True)
    edit = DB.Column(DB.Integer, nullable=False)

    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"),
                        nullable=False)

    uuid = DB.Column(DB.String(40), nullable=False)

    # pylint: disable=line-too-long
    # https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.choice
    # pylint: enable=line-too-long
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
    edit = DB.Column(DB.Integer, nullable=False)

    node_id = DB.Column(DB.Integer, DB.ForeignKey("firewall.id"),
                        nullable=False)

    uuid = DB.Column(DB.String(40), nullable=False)  # UUID
    name = DB.Column(DB.String(50))  # Optional
    comments = DB.Column(DB.String(50))  # Optional

    # pylint: disable=line-too-long
    # https://docs.sqlalchemy.org/en/13/orm/join_conditions.html#handling-multiple-join-paths
    # pylint: enable=line-too-long
    srcintf_id = DB.Column(DB.Integer, DB.ForeignKey("interface.id"))
    srcintf = DB.relationship("Interface", foreign_keys=[srcintf_id])

    dstintf_id = DB.Column(DB.Integer, DB.ForeignKey("interface.id"))
    dstintf = DB.relationship("Interface", foreign_keys=[dstintf_id])

    # firewall addrgrp or firewall address{,6}
    srcaddr_group_id = DB.Column(DB.Integer,
                                 DB.ForeignKey("firewall_address_grp.id"))
    srcaddr_group = DB.relationship("FirewallAddressGrp",
                                    foreign_keys=[srcaddr_group_id])
    srcaddr_id = DB.Column(DB.Integer, DB.ForeignKey("firewall_address.id"))
    srcaddr = DB.relationship("FirewallAddress", foreign_keys=[srcaddr_id])

    dstaddr_group_id = DB.Column(DB.Integer,
                                 DB.ForeignKey("firewall_address_grp.id"))
    dstaddr_group = DB.relationship("FirewallAddressGrp",
                                    foreign_keys=[dstaddr_group_id])
    dstaddr_id = DB.Column(DB.Integer, DB.ForeignKey("firewall_address.id"))
    dstaddr = DB.relationship("FirewallAddress", foreign_keys=[dstaddr_id])

    # firewwall service group or firewall_policy service custom
    serivce_group_id = DB.Column(DB.Integer,
                                 DB.ForeignKey("firewall_service_group.id"))
    serivce_group = DB.relationship("FirewallServiceGroup")
    serivce_custom_id = DB.Column(DB.Integer,
                                  DB.ForeignKey("firewall_service_custom.id"))
    serivce_custom = DB.relationship("FirewallServiceCustom")

    logtraffic = DB.Column(DB.String(10))
    schedule = DB.Column(DB.String(10), default="always")
    status = DB.Column(DB.String(10))

    action = DB.Column(sqlalchemy_utils.ChoiceType(FW_ACTION_TYPES),
                       default=FW_ACTION_TYPES[0][0])

# vim:sw=4:ts=4:et:
