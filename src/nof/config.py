#
# Copyright (C) 2020 Satoru SATOh <ssato@redhat.com>
# SPDX-License-Identifier: MIT
#
# pylint: disable=too-few-public-methods
"""Default config
"""
from __future__ import absolute_import

import os.path
import os
import uuid


NOF_DATA_DIR = "/var/lib/nof"
NOF_DATA_DIR_FOR_TESTS = "/tmp/nof"


class Config():
    """Default configuration
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(uuid.uuid4())
    WTF_CSRF_ENABLED = True

    # .. seealso:: https://pythonhosted.org/Flask-Uploads/
    _datadir = NOF_DATA_DIR
    UPLOADED_FILES_DEST = os.path.join(_datadir, "uploads")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(_datadir, "main.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Limit the size of file to upload: 500 [MB]
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024

    @staticmethod
    def init_app(app):
        """Initialize application.
        """
        keys = ("NOF_UPLOADDIR", "SQLALCHEMY_DATABASE_URI")
        for key in keys:
            if key in os.environ:
                setattr(app, key, os.environ[key])


class DevelopmentConfig(Config):
    """
    Config for development.
    """
    DEBUG = True
    UPLOADED_FILES_DEST = os.path.join(NOF_DATA_DIR_FOR_TESTS, "uploads")
    SQLALCHEMY_DATABASE_URI = ("sqlite:///" +
                               os.path.join(NOF_DATA_DIR_FOR_TESTS, "main.db"))

    if not os.path.exists(UPLOADED_FILES_DEST):
        os.mkdir(UPLOADED_FILES_DEST)


class TestingConfig(Config):
    """
    Config for testing.
    """
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Config for production.
    """

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


CNF = dict(development=DevelopmentConfig,
           testing=TestingConfig,
           production=ProductionConfig,
           default=DevelopmentConfig)

# vim:sw=4:ts=4:et:
