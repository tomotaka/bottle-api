#!/usr/bin/python
# -*- coding: utf-8 -*-


class WebApiError(Exception):
    def __init__(self, message, status=500, result=None):
        self.message = message
        self.status = status
        self.result = result

    def __str__(self):
        return self.message


class AbstractSuccessDataFormatter(object):
    def format(self, result):
        raise NotImplementedError()


class AbstractErrorDataFormatter(object):
    def format(self, exception_obj):
        raise NotImplementedError()


class AbstractResponseBuilder(object):
    def build_success(self, result):
        raise NotImplementedError()

    def build_error(self, exception_obj):
        raise NotImplementedError()
