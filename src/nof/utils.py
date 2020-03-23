#
# Copyright (C) 2020 Satoru SATOh <ssato@redhat.com>
# SPDX-License-Identifier: MIT
#
"""Global utility routines
"""
import os.path
import os

from .globals import NOF_DATA_DIR


def datadir_maybe_from_env():
    """
    :return: data top dir of this app
    """
    return os.environ.get("NOF_DATA_DIR", NOF_DATA_DIR)


def uploaddir(datadir=None):
    """
    >>> uploaddir()
    '/var/lib/nof/uploads'
    >>> uploaddir("/tmp/nof")
    '/tmp/nof/uploads'
    """
    if datadir is None:
        datadir = datadir_maybe_from_env()

    return os.path.join(datadir, "uploads")


def database_url(datadir=None):
    """
    >>> database_url()
    'sqlite:////var/lib/nof/main.db'
    """
    if datadir is None:
        datadir = datadir_maybe_from_env()

    return "sqlite:///" + os.path.join(datadir, "main.db")

# vim:sw=4:ts=4:et:
