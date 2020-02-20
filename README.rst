================================
NOF - Network Objects Finder
================================

.. image:: https://img.shields.io/travis/ssato/nof
      :target: https://travis-ci.org/ssato/nof
   :alt: [Test status]

.. TODO:
.. .. image:: https://scrutinizer-ci.com/g/ssato/nof/badges/quality-score.png?b=master
      :target: https://scrutinizer-ci.com/g/ssato/nof
   :alt: [Code Quality by Scrutinizer]

.. .. image:: https://img.shields.io/lgtm/grade/python/g/ssato/nof.svg
      :target: https://lgtm.com/projects/g/ssato/nof/context:python
   :alt: [Code Quality by LGTM]

About
=======

NOF, network objects finder is an web application to search various 'objects'
in networks consists of various networking nodes have IP address.

- Author: Satoru SATOH <ssato@redhat.com>
- License: MIT

Disclaimer
============

This is a very experimental prototype web application implementation to
research possibility of web application assists network engineers. This is not
intended to use in production nor a supported Red Hat product at all. Please
use this software at your own risk.

Installation
===============

Requirements
-------------

See pkg/requirements.txt.

Build and Installation
=======================

Build RPM
------------

Try:

- python3 setup.py bdist_rpm --source-only
- mock dist/python-nof-*.rpm

Unfortunatelly, some RPMs are not available and you need to build themselves
along with this, so I recommend the later way.

Install
----------

Try 'pip3 install --root /path/to/install/dir .' in the top source dir.


Run and tests
================

Tests
--------

Try 'tox -e py37' for example.

Run app
---------

Try 'tox -e app' to run this application locally.

.. vim:sw=2:ts=2:et:
