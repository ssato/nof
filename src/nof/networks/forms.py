"""HTML Forms for networks app.

SPDX-License-Identifier: MIT

References:
  - Flask-WTF: https://flask-wtf.readthedocs.org
  - Flask-Uploads: https://pythonhosted.org/Flask-Uploads/
"""
from __future__ import absolute_import

import flask_wtf.file
import flask_wtf
import wtforms.validators
import wtforms

from ..globals import NODE_TYPES, NODE_ANY


class UploadNetworksForm(flask_wtf.FlaskForm):
    """
    Form to upload networks JSON data files.
    """
    upload = flask_wtf.file.FileField(u"Network JSON data", validators=[
        flask_wtf.file.FileRequired(),
        flask_wtf.file.FileAllowed(("json", "js"), u"JSON data only!")
    ])
    submit = wtforms.SubmitField("Upload")


class FindNetworksForm(flask_wtf.FlaskForm):
    """
    Form to find networks by IP address
    """
    ip = wtforms.StringField(u"IP Address", validators=[
        wtforms.validators.InputRequired(),
        wtforms.validators.IPAddress()
    ])
    submit = wtforms.SubmitField("Find Networks")


class FindNetworkPathsForm(flask_wtf.FlaskForm):
    """Form to input src ip address.
    """
    src_ip = wtforms.StringField(u"Src IP Address", validators=[
        wtforms.validators.InputRequired(),
        wtforms.validators.IPAddress()
    ])

    dst_ip = wtforms.StringField(u"Dest IP Address", validators=[
        wtforms.validators.InputRequired(),
        wtforms.validators.IPAddress()
    ])

    ntype_pairs = [(k, k.title()) for k in NODE_TYPES]
    find_type = wtforms.SelectField(u"Node Type", choices=ntype_pairs,
                                    default=NODE_ANY)
    submit = wtforms.SubmitField("Find Network Paths")

# vim:sw=4:ts=4:et:
