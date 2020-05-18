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

from . import utils


class Config():
    """Default configuration
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(uuid.uuid4())
    WTF_CSRF_ENABLED = True

    # Limit the size of file to upload: 500 [MB]
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024

    def __init__(self, datadir=None):
        """Initialize defaults
        """
        # pylint: disable=invalid-name
        # .. seealso:: https://pythonhosted.org/Flask-Uploads/
        self.UPLOADED_FILES_DEST = utils.uploaddir(datadir)
        # pylint: enable=invalid-name

    def init_app(self, app):
        """Initialize application.
        """
        keys = ("UPLOADED_FILES_DEST", )
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
        if "NOF_DATA_DIR" not in os.environ:
            os.environ["NOF_DATA_DIR"] = "/tmp/nof/"

    cnfs = dict(development=DevelopmentConfig,
                testing=TestingConfig,
                production=ProductionConfig,
                default=DevelopmentConfig)

    return cnfs[name]()

# vim:sw=4:ts=4:et:
