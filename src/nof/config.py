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

from .utils import uploaddir, database_url


class Config():
    """Default configuration
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(uuid.uuid4())
    WTF_CSRF_ENABLED = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Limit the size of file to upload: 500 [MB]
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024

    def __init__(self, datadir=None):
        """Initialize defaults
        """
        # pylint: disable=invalid-name
        # .. seealso:: https://pythonhosted.org/Flask-Uploads/
        self.UPLOADED_FILES_DEST = uploaddir(datadir)
        self.SQLALCHEMY_DATABASE_URI = database_url(datadir)
        # pylint: enable=invalid-name

    def init_app(self, app):
        """Initialize application.
        """
        keys = ("UPLOADED_FILES_DEST", "SQLALCHEMY_DATABASE_URI")
        for key in keys:
            setattr(app, key, getattr(self, key))


class DevelopmentConfig(Config):
    """
    Config for development.
    """
    DEBUG = True


class TestingConfig(DevelopmentConfig):
    """
    Config for testing.
    """
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Config for production.
    """
    TESTING = False

    def init_app(self, app):
        """Ensure workdir exists.
        """
        if not os.path.exists(self.UPLOADED_FILES_DEST):
            os.makedirs(self.UPLOADED_FILES_DEST)


def get_config(name="development"):
    """
    :return: An instance of *Config
    """
    if name in ("development", "testing"):
        os.environ["NOF_DATA_DIR"] = "/tmp/nof/"

    cnfs = dict(development=DevelopmentConfig,
                testing=TestingConfig,
                production=ProductionConfig,
                default=DevelopmentConfig)

    return cnfs[name]()

# vim:sw=4:ts=4:et:
