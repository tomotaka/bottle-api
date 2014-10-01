#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import bottle

try:
    import simplejson as json
except ImportError:
    import json

from bottleapi import (
    WebApiError,
    AbstractSuccessDataFormatter,
    AbstractErrorDataFormatter,
    AbstractResponseBuilder
)


class JsonSuccessDataFormatter(AbstractSuccessDataFormatter):
    def format(self, result):
        return json.dumps(dict(status='ok', result=result))


class JsonErrorDataFormatter(AbstractErrorDataFormatter):
    def format(self, exception_obj):
        message = str(exception_obj)
        result = exception_obj.result if hasattr(exception_obj, 'result') else None
        return json.dumps(dict(status='error', result=result, message=message))


class JsonResponseBuilder(AbstractResponseBuilder):
    def __init__(
            self,
            enable_jsonp=True,
            jsonp_parameter='j',
            suc_formatter=None,
            err_formatter=None):
        self._suc_formatter = suc_formatter or JsonSuccessDataFormatter()
        self._err_formatter = err_formatter or JsonErrorDataFormatter()
        self._enable_jsonp = enable_jsonp
        self._jsonp_parameter = jsonp_parameter

    def _get_jsonp_name(self, request):
        if not self._enable_jsonp:
            return None
        return request.params.get(self._jsonp_parameter, None)

    def _is_jsonp(self, request):
        if not self._enable_jsonp:
            return False

        jsonp_name = self._get_jsonp_name(request)
        return jsonp_name is not None

    def _wrap_if_jsonp(self, body, request):
        if not self._enable_jsonp:
            return body

        jsonp_name = self._get_jsonp_name(request)
        return '%s(%s);' % (jsonp_name, body) if jsonp_name else body

    def _add_headers(self, response, request):
        content_type = 'application/javascript' if self._is_jsonp(request) else 'application/json'

        response.set_header('Content-Type', content_type)
        response.set_header('Cache-Control', 'no-cache')
        response.set_header('Pragma', 'no-cache')

    def _build_response(self, body, status, request):
        response = bottle.HTTPResponse(status=status, body=body)
        self._add_headers(response, request)
        return response

    def build_success(self, result, request):
        body = self._suc_formatter.format(result)
        body = self._wrap_if_jsonp(body, request)
        return self._build_response(body, 200, request)

    def build_error(self, exception_obj, request):
        status = 500
        if hasattr(exception_obj, 'status'):
            status = exception_obj.status

        body = self._err_formatter.format(exception_obj)
        body = self._wrap_if_jsonp(body, request)
        return self._build_response(body, status, request)


def build_json_endpoint_decorator(
        enable_jsonp=True,
        jsonp_parameter='j',
        suc_fmtr=None,
        err_fmtr=None,
        logger=None):
    logger = logger or logging.getLogger()

    r_builder = JsonResponseBuilder(
        enable_jsonp=enable_jsonp,
        jsonp_parameter=jsonp_parameter,
        suc_formatter=suc_fmtr,
        err_formatter=err_fmtr
    )

    def _decorator(func):
        def _decorated_func(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except WebApiError as e:
                # expectable error
                return r_builder.build_error(e, bottle.request)
            except Exception as e:
                # unexpected error
                logger.exception(e)
                return r_builder.build_error(e, bottle.request)
            else:
                # no error
                return r_builder.build_success(result, bottle.request)

        _decorated_func.__name__ = func.__name__
        return _decorated_func

    return _decorator


# default decorator
json_endpoint = build_json_endpoint_decorator()
