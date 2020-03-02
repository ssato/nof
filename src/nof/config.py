#
# Copyright (C) 2020 Satoru SATOh <ssato@redhat.com>
# SPDX-License-Identifier: MIT
#
# pylint: disable=too-few-public-methods
"""Default config
"""
from __future__ import absolute_import

import os
import uuid


class Config():
    """Default configuration
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(uuid.uuid4())
    WTF_CSRF_ENABLED = True

    # .. seealso:: https://pythonhosted.org/Flask-Uploads/
    _datadir = "/var/lib/nof/"
    UPLOADED_FILES_DEST = os.path.join(_datadir, "uploads")

    # Limit the size of file to upload: 500 [MB]
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024

    @staticmethod
    def init_app(app):
        """Initialize application.
        """
        key = "NOF_UPLOADDIR"
        if key in os.environ:
            app.UPLOADED_FILES_DEST = os.environ[key]


class DevelopmentConfig(Config):
    """
    Config for development.
    """
    DEBUG = True
    UPLOADED_FILES_DEST = "/tmp/nof_uploads"

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
