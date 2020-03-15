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

        iface = TT.Interface(vdom=vdom, type="physical",
                             vlanforward="enable",
                             allowaccess="ping",
                             alias="Libvirt_Default_GW",
                             snmp_index=9,
                             ip="192.168.122.1 255.255.255.0")
        firewall.interfaces.append(iface)

        # with self.app.app_context():
        nof.db.DB.session.add(firewall)

        self.assertEqual(len(firewall.vdoms), 1)
        self.assertEqual(len(firewall.interfaces), 1)

# vim:sw=4:ts=4:et:
