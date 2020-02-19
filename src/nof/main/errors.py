"""Error pages.
"""
import flask

from . import APP


def _error_handler(msg, ecode, template="error.html"):
    """
    An wrapper of flask.render_template
    """
    if flask.request.accept_mimetypes.accept_json and \
            not flask.request.accept_mimetypes.accept_html:
        resp = flask.jsonify(dict(error=msg))
        resp.status_code = ecode
        return resp

    err = "%d %s" % (ecode, msg.title())
    return flask.render_template(template, error=err), ecode


@APP.app_errorhandler(404)
def page_not_found(err):
    """404 error page"""
    return _error_handler("not found: {}".format(str(err)), 404)


@APP.app_errorhandler(500)
def internal_server_error(err):
    """500 error page"""
    return _error_handler("internal server error: {}".format(str(err)),
                          500)

# vim:sw=4:ts=4:et:
