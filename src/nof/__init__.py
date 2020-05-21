#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
r"""Entrypoint of this app.
"""
from .init import create_app
from . import config, main, fortios, networks


__version__ = "0.2.0"

# vim:sw=4:ts=4:et:
