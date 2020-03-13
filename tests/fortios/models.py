#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import nof
import nof.config
import nof.db
import nof.lib.fortios as F
from .. import common as C


class Models_10_TestCase(C.BluePrintTestCaseWithWorkdir):

    maxDiff = None
    cleanup = False

    def setUp(self):
        super(Models_10_TestCase, self).setUp()
        # with self.app.app_context():
        # nof.db.DB.create_all()

    def tearDown(self):
        super(Models_10_TestCase, self).tearDown()
        C.prune_workdir(nof.config.NOF_DATA_DIR_FOR_TESTS)

    def test_10_insert_model_data(self):
        C.skip_test()  # .. todo::

        nof.db.DB.create_all()
        firewall = F.Firewall(name="abc012", info="fortios test node")

        vdom = F.VDom()
        firewall.vdoms.append(vdom)

        iface = nof.fortios.Interface(vdom=vdom, type="physical",
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
