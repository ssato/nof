#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import nof.db
import nof.fortios as TT

from .. import common as C


class Models_10_TestCase(C.BluePrintTestCaseWithWorkdir):

    maxDiff = None

    def test_10_insert_model_data(self):
        firewall = TT.Firewall(name="abc012", info="fortios test node")

        vdom = TT.VDom()
        firewall.vdoms.append(vdom)

        iface_1 = TT.Interface(edit="mgmt",
                               vdom=vdom, type="physical",
                               allowaccess="ping https ssh snmp",
                               alias="Management GW",
                               snmp_index=1,
                               dedicated_to="management",
                               ip="10.0.1.1 255.255.255.0",
                               trust_ip_1="10.0.1.254 255.255.255.0")
        iface_2 = TT.Interface(edit="port1",
                               vdom=vdom, type="physical",
                               vlanforward="enable",
                               allowaccess="ping",
                               alias="Libvirt_Default_GW",
                               snmp_index=9,
                               ip="192.168.122.1 255.255.255.0")
        firewall.interfaces.append(iface_1)
        firewall.interfaces.append(iface_2)

        svc_cat_1 = TT.FirewallServiceCategory(edit="Web Access",
                                               comment="web access")
        firewall.firewall_service_categories.append(svc_cat_1)

        svc_cat_2 = TT.FirewallServiceCategory(edit="Network Services",
                                               comment="network services")
        firewall.firewall_service_categories.append(svc_cat_2)

        svc_cus_1 = TT.FirewallServiceCustom(edit="DNS",
                                             category=svc_cat_2,
                                             tcp_portrange="53",
                                             udp_portrange="53")

        svc_cus_2 = TT.FirewallServiceCustom(edit="HTTP",
                                             category=svc_cat_1,
                                             tcp_portrange="80")

        svc_cus_3 = TT.FirewallServiceCustom(edit="HTTPS",
                                             category=svc_cat_1,
                                             tcp_portrange="443")
        firewall.firewall_service_customs.append(svc_cus_1)
        firewall.firewall_service_customs.append(svc_cus_2)
        firewall.firewall_service_customs.append(svc_cus_3)

        svc_grp = TT.FirewallServiceGroup(edit="Web Access",
                                          comment="Web Access")
        svc_grp.member.append(svc_cus_1)
        svc_grp.member.append(svc_cus_2)
        svc_grp.member.append(svc_cus_3)
        firewall.firewall_service_groups.append(svc_grp)

        addr_1 = TT.FirewallAddress(edit="google", uuid=C.uuid_gen(),
                                    type="wildcard-fqdn",
                                    wildcard_fqdn="*.google.com")
        addr_2 = TT.FirewallAddress(edit="amazon", uuid=C.uuid_gen(),
                                    type="wildcard-fqdn",
                                    wildcard_fqdn="*.amazon.com")
        addr_3 = TT.FirewallAddress(edit="facebook", uuid=C.uuid_gen(),
                                    type="wildcard-fqdn",
                                    wildcard_fqdn="*.facebook.com")
        addr_4 = TT.FirewallAddress(edit="apple", uuid=C.uuid_gen(),
                                    type="wildcard-fqdn",
                                    wildcard_fqdn="*.apple.com")
        addr_5 = TT.FirewallAddress(edit="N_10.0.1.0", uuid=C.uuid_gen(),
                                    comment="Management Network",
                                    associated_interface=iface_1,
                                    subnet="10.0.1.0 255.255.255.0")
        addr_6 = TT.FirewallAddress(edit="H_192.168.122.1", uuid=C.uuid_gen(),
                                    comment="Libvirt_Default_GW",
                                    associated_interface=iface_2,
                                    subnet="192.168.122.1 255.255.255.0")

        firewall.firewall_addresses.append(addr_1)
        firewall.firewall_addresses.append(addr_2)
        firewall.firewall_addresses.append(addr_3)
        firewall.firewall_addresses.append(addr_4)
        firewall.firewall_addresses.append(addr_5)
        firewall.firewall_addresses.append(addr_6)

        addr_grp_1 = TT.FirewallAddressGrp(edit="GAFA", uuid=C.uuid_gen(),
                                           comment="GAFA")
        addr_grp_2 = TT.FirewallAddressGrp(edit="GAFA", uuid=C.uuid_gen(),
                                           comment="GAFA")
        addr_grp_1.member.append(addr_1)
        addr_grp_1.member.append(addr_2)
        addr_grp_1.member.append(addr_3)
        addr_grp_1.member.append(addr_4)
        addr_grp_2.member.append(addr_5)
        firewall.firewall_addrgrps.append(addr_grp_1)

        policy_1 = TT.FirewallPolicy(edit="block GAFA", uuid=C.uuid_gen(),
                                     srcintf=iface_1, dstintf=iface_2,
                                     srcaddr_group=addr_grp_2,
                                     dstaddr_group=addr_grp_1,
                                     service_group=svc_grp,
                                     schedule="always", logtraffic="all",
                                     action="accept", status="disable")
        firewall.firewall_policies.append(policy_1)

        # with self.app.app_context():
        nof.db.DB.session.add(firewall)

        self.assertEqual(len(firewall.vdoms), 1)
        self.assertTrue(len(firewall.interfaces) > 1)

# vim:sw=4:ts=4:et:
