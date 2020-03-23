#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import sqlalchemy.sql
import nof.db

from .. import common as C


class Test(C.BluePrintTestCaseWithWorkdir):

    maxDiff = None

    def test_set_sqlite_pragma(self):
        query = sqlalchemy.sql.text("PRAGMA foreign_keys")
        res = [r for r in nof.db.DB.session.execute(query)]
        self.assertTrue(res[0][0], 1)  # It should be set to true.

# vim:sw=4:ts=4:et:
