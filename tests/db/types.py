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

    def test_10_IPNetworkType(self):
        
        class Network(self.base):
            __tablename__ = "networks"

            id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True,
                                   primary_key=True)
            addr = sqlalchemy.Column(TT.IPNetworkType)

            def __repr__(self):
                return ("<Network(id={!s}, "
                        "addr={!s})>".format(self.id, self.addr))

        self.base.metadata.create_all(self.engine)

        addr_1 = "10.0.0.0/8"
        net_1 = Network(addr=addr_1)

        session = sqlalchemy.orm.sessionmaker(bind=self.engine)()
        session.add(net_1)
        session.commit()

        self.assertEqual(net_1.addr, TT.ipaddress.ip_network(addr_1))

        net = session.query(Network).filter_by(addr=addr_1).first()
        self.assertTrue(net is net_1, net)
        self.assertTrue(net.addr,  TT.ipaddress.ip_network(addr_1))

# vim:sw=4:ts=4:et:
