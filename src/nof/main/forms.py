"""HTML Forms.

License: MIT

References:
  - Flask-WTF: https://flask-wtf.readthedocs.org
  - Flask-Uploads: https://pythonhosted.org/Flask-Uploads/
"""
from __future__ import absolute_import

import flask_wtf.file
import flask_wtf
import wtforms.validators
import wtforms

from nof.globals import NODE_TYPES


NODE_TYPE_PAIRS = [(k, k.title()) for k in NODE_TYPES]


class UploadForm(flask_wtf.FlaskForm):
    """Form to upload graph data.
    """
    upload = flask_wtf.file.FileField(u"Network YAML data", validators=[
        flask_wtf.file.FileRequired(),
        flask_wtf.file.FileAllowed(("yaml", "yml"), u"YAML data only!")
    ])
    submit = wtforms.SubmitField("Upload")


class NetworkFinderForm(flask_wtf.FlaskForm):
    """Form to input src ip address.
    """
    ip = wtforms.StringField(u"IP Address", validators=[
        wtforms.validators.InputRequired(),
        wtforms.validators.IPAddress()
    ])
    submit = wtforms.SubmitField("Find Network")


class PathFinderForm(flask_wtf.FlaskForm):
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

    find_type = wtforms.SelectField(u"Object Type", choices=NODE_TYPE_PAIRS,
                                    default=NODE_TYPES[0])
    submit = wtforms.SubmitField("Find")

# vim:sw=4:ts=4:et:
