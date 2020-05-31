#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=unused-import
r"""Entrypoint of this app.
"""
from .init import create_app  # noqa: F401
from . import config  # noqa: F401


__version__ = "0.2.0"

# vim:sw=4:ts=4:et:
