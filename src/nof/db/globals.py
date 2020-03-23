#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Globals
"""
import flask_sqlalchemy
import sqlalchemy.engine
import sqlalchemy


DB = flask_sqlalchemy.SQLAlchemy()


@sqlalchemy.event.listens_for(sqlalchemy.engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    """
    https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#foreign-key-support
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# vim:sw=4:ts=4:et:
