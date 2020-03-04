#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Utility functions
"""
import os.path
import os


def ensure_dir_exists(filepath):
    """Ensure dir for filepath exists
    """
    tdir = os.path.dirname(filepath)

    if not os.path.exists(tdir):
        os.makedirs(tdir)

# vim:sw=4:ts=4:et:
