#!/usr/bin/python
# -*- coding: utf-8 -*-
from unittest import TestCase
from nose.tools import eq_, raises

from bottleapi import (
    WebApiError,
    AbstractSuccessDataFormatter,
    AbstractErrorDataFormatter,
    AbstractResponseBuilder
)


class BottleApiGeneralTestCase(TestCase):
    def test_web_api_error(self):
        e1 = WebApiError('message-test1')
        eq_(e1.message, 'message-test1')
        eq_(e1.status, 500)
        eq_(e1.result, None)

        e2 = WebApiError('message-test2', 400)
        eq_(e2.message, 'message-test2')
        eq_(e2.status, 400)
        eq_(e2.result, None)

        e3 = WebApiError('msg-test3', 403, 123)
        eq_(e3.message, 'msg-test3')
        eq_(e3.status, 403)
        eq_(e3.result, 123)

    @raises(NotImplementedError)
    def test_abstract_success_data_formatter(self):
        f = AbstractSuccessDataFormatter()
        f.format(None)

    @raises(NotImplementedError)
    def test_abstract_error_data_formatter(self):
        f = AbstractErrorDataFormatter()
        f.format(None)

    @raises(NotImplementedError)
    def test_abstract_response_builder_build_success(self):
        b = AbstractResponseBuilder()
        b.build_success(None)

    @raises(NotImplementedError)
    def test_abstract_response_builder_build_error(self):
        b = AbstractResponseBuilder()
        b.build_error(None)
