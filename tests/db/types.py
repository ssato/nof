#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import unittest

import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm

import nof.db.types as TT


class TestCustomTypes(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:", echo=True)
        self.base = sqlalchemy.ext.declarative.declarative_base()

    def test_10_FortiosSubnetType(self):
        class Subnet(self.base):
            __tablename__ = "subnet"

            id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True,
                                   primary_key=True)
            addr = sqlalchemy.Column(TT.FortiosSubnetType)

            def __repr__(self):
                return ("<Network(id={!s}, "
                        "addr={!s})>".format(self.id, self.addr))

        self.base.metadata.create_all(self.engine)

        addr_1 = "10.0.0.0 255.0.0.0"
        net_1 = Subnet(addr=addr_1)
        iif_1 = TT.ipaddress.ip_interface(addr_1.replace(' ', '/'))

        session = sqlalchemy.orm.sessionmaker(bind=self.engine)()
        session.add(net_1)
        session.commit()

        self.assertEqual(net_1.addr, iif_1)

        net = session.query(Subnet).filter_by(addr=addr_1).first()
        self.assertTrue(net is net_1, net)
        self.assertTrue(net.addr, iif_1)

        addr_2 = "192.168.122.7 255.255.255.0"
        net_2 = Subnet(addr=addr_2)
        iif_2 = TT.ipaddress.ip_interface(addr_2.replace(' ', '/'))

        session.add(net_2)
        session.commit()

        self.assertEqual(net_2.addr, iif_2)

        net = session.query(Subnet).filter_by(addr=addr_2).first()
        self.assertTrue(net is net_2, net)
        self.assertTrue(net.addr, iif_2)

# vim:sw=4:ts=4:et:
