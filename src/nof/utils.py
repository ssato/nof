#
# Copyright (C) 2020 Satoru SATOh <ssato@redhat.com>
# SPDX-License-Identifier: MIT
#
"""Global utility routines
"""
import functools
import glob
import hashlib
import os.path
import os

import werkzeug

from . import globals


def datadir_maybe_from_env():
    """
    :return: data top dir of this app
    """
    return os.environ.get("NOF_DATA_DIR", globals.NOF_DATA_DIR)


def uploaddir(file_type, datadir=None):
    """
    :param file_type: type of file to upload
    :param datadir: top dir to save data files

    >>> uploaddir("foo")
    '/var/lib/nof/uploads/foo'
    >>> uploaddir("bar", "/tmp/nof")
    '/tmp/nof/uploads/bar'
    """
    if datadir is None:
        datadir = datadir_maybe_from_env()

    return os.path.join(datadir, "uploads", file_type)


@functools.lru_cache(maxsize=32)
def checksum(filepath=None, content=None, encoding="utf-8",
             hash_fn=hashlib.sha1):
    """
    Compute the checksum of given file, `filepath`

    :param filepath: Absolute path to the file to compuste its checksum
    :param content: The content of the file
    :param encoding: Character set encoding of the file
    :param hash_fn: Hash algorithm to compute the checksum

    :return: A str gives the checksum value of the given file's content
    """
    if content is None:
        if filepath is None:
            raise ValueError("Either `filepath` or `content` must be given!")

        # .. note::
        #    We don't need to worry about the size of files uploaded
        #    because we use Flask-Uploads and it should limit the size of
        #    files to upload.
        content = open(filepath).read()

    return hash_fn(content.encode(encoding)).hexdigest()


def uploaded_filename(filename, content=None):
    """
    Compute a new file name for the file to upload based on its filename and
    content in a consistent way.

    :param filename: Original maybe unsecure file name
    :param content: File's content

    :return: A str gives a file name
    """
    fbase = werkzeug.utils.secure_filename(filename)
    if content is None:
        return fbase  # It's the name of uploaded file.

    chksm = checksum(content=content)  # filepath is not fixed yet.

    return "{}-{}".format(fbase, chksm)


def uploaded_filepath(filename, file_type, content=None, datadir=None):
    """
    Compute a consisten path of the file to save content from uploaded file
    based on its filename and content.

    :param filename:
        The name of the original maybe unsecure file or uploaded file. In the
        former case, the content of the file must be given also.

    :param file_type: type of file to upload
    :param content: The content (str) of the file
    :param datadir: top dir to save data files

    :return: A str gives a absolute file path
    """
    fname = uploaded_filename(filename, content=content)
    udir = uploaddir(file_type, datadir=datadir)

    return os.path.join(udir, fname)


def ensure_dir_exists(filepath):
    """Ensure dir for filepath exists
    """
    tdir = os.path.dirname(filepath)

    if not os.path.exists(tdir):
        os.makedirs(tdir)


def list_filenames(pattern=None, datadir=None):
    """
    :param pattern: Filename pattern [*.yml]
    :param datadir: top dir to save data files

    :return: A list of data files in given `datadir`.
    """
    if pattern is None:
        pattern = "*.json"

    files = glob.glob(os.path.join(datadir, pattern))
    return sorted(os.path.basename(f) for f in files)


def list_uploaded_filenames(file_type, pattern=None, datadir=None):
    """
    :param file_type: type of file to upload
    :param pattern: Filename pattern [*.yml]
    :param datadir: top dir to save data files

    :return: A list of data files in given `datadir`.
    """
    udir = uploaddir(file_type, datadir=datadir)
    return list_filenames(pattern=pattern, datadir=udir)

# vim:sw=4:ts=4:et:
