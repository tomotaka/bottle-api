#!/usr/bin/python
# -*- coding: utf-8 -*-
from unittest import TestCase
from nose.tools import eq_
from webtest import TestApp

from bottle import Bottle

from bottleapi import WebApiError
from bottleapi.jsonapi import (
    JsonSuccessDataFormatter,
    JsonErrorDataFormatter,
    JsonResponseBuilder,
    json_endpoint
)


class MockRequest(object):
    def __init__(self):
        self.params = dict()


class JsonSuccessDataFormatterTestCase(TestCase):
    def test_format(self):
        f = JsonSuccessDataFormatter()

        v = dict(a=100, b='hoge')
        result = f.format(v)
        eq_(result, '{"status": "ok", "result": {"a": 100, "b": "hoge"}}')


class JsonErrorDataFormatterTestCase(TestCase):
    def test_format(self):
        f = JsonErrorDataFormatter()

        e1 = WebApiError('hogege')
        result1 = f.format(e1)
        eq_(result1, '{"status": "error", "message": "hogege", "result": null}')

        e2 = WebApiError('mogera', result=100)
        result2 = f.format(e2)
        eq_(result2, '{"status": "error", "message": "mogera", "result": 100}')


class JsonResponseBuilderTestCase(TestCase):
    def test_build_success(self):
        b1 = JsonResponseBuilder()

        mr1 = MockRequest()
        mr1.params = {
            'hoge': 'hogege'
        }
        v1 = {'mogera': 'moge'}

        result1 = b1.build_success(v1, mr1)
        eq_(result1.status_code, 200)
        eq_(result1.body, '{"status": "ok", "result": {"mogera": "moge"}}')
        eq_(result1.get_header('Content-Type'), 'application/json')
        eq_(result1.get_header('Pragma'), 'no-cache')
        eq_(result1.get_header('Cache-Control'), 'no-cache')

        mr2 = MockRequest()
        mr2.params = {
            'j': 'j123',
            'hoge': 'hogege'
        }
        v2 = {'a': 'bb'}
        result2 = b1.build_success(v2, mr2)
        eq_(result2.status_code, 200)
        eq_(result2.body, 'j123({"status": "ok", "result": {"a": "bb"}});')
        eq_(result2.get_header('Content-Type'), 'application/javascript')
        eq_(result2.get_header('Pragma'), 'no-cache')
        eq_(result2.get_header('Cache-Control'), 'no-cache')

    def test_build_error(self):
        b1 = JsonResponseBuilder()

        mr1 = MockRequest()
        e1 = WebApiError('error1', status=500, result=None)
        result1 = b1.build_error(e1, mr1)
        eq_(result1.status_code, 500)
        eq_(result1.body, '{"status": "error", "message": "error1", "result": null}')
        eq_(result1.get_header('Content-Type'), 'application/json')
        eq_(result1.get_header('Pragma'), 'no-cache')
        eq_(result1.get_header('Cache-Control'), 'no-cache')

        mr2 = MockRequest()
        mr2.params = {
            'j': 'j234',
            'hoge': 'hogege'
        }
        e2 = WebApiError('error098', status=403, result='abcd')
        result2 = b1.build_error(e2, mr2)
        eq_(result2.status_code, 403)
        eq_(result2.body, 'j234({"status": "error", "message": "error098", "result": "abcd"});')
        eq_(result2.get_header('Content-Type'), 'application/javascript')
        eq_(result2.get_header('Pragma'), 'no-cache')
        eq_(result2.get_header('Cache-Control'), 'no-cache')


class JsonEndPointDecoratorTestCase(TestCase):
    def test_success_response_case(self):
        def _success_response_func1():
            return dict(value=123)

        decorated1 = json_endpoint(_success_response_func1)

        app1 = Bottle()
        app1.route('/', ['GET'], decorated1)

        wt1 = TestApp(app1)
        resp1 = wt1.get('/', status=200)

        eq_(resp1.status_int, 200)
        eq_(resp1.content_type, 'application/json')
        eq_(resp1.body, '{"status": "ok", "result": {"value": 123}}')
        eq_(resp1.headers['Pragma'], 'no-cache')
        eq_(resp1.headers['Cache-Control'], 'no-cache')

        # test JSONP
        resp2 = wt1.get('/', params=dict(j='j345'), status=200)
        eq_(resp2.status_int, 200)
        eq_(resp2.content_type, 'application/javascript')
        eq_(resp2.body, 'j345({"status": "ok", "result": {"value": 123}});')
        eq_(resp2.headers['Pragma'], 'no-cache')
        eq_(resp2.headers['Cache-Control'], 'no-cache')

    def test_error_response_case(self):
        def _error_response_func1():
            raise WebApiError('fail567', status=500, result=None)

        decorated1 = json_endpoint(_error_response_func1)

        app1 = Bottle()
        app1.route('/', ['GET'], decorated1)

        wt1 = TestApp(app1)
        resp1 = wt1.get('/', status=500)

        eq_(resp1.status_int, 500)
        eq_(resp1.content_type, 'application/json')
        eq_(resp1.body, '{"status": "error", "message": "fail567", "result": null}')
        eq_(resp1.headers['Pragma'], 'no-cache')
        eq_(resp1.headers['Cache-Control'], 'no-cache')

        # test JSONP
        resp2 = wt1.get('/', params=dict(j='j345'), status=500)
        eq_(resp2.status_int, 500)
        eq_(resp2.content_type, 'application/javascript')
        eq_(resp2.body, 'j345({"status": "error", "message": "fail567", "result": null});')
        eq_(resp2.headers['Pragma'], 'no-cache')
        eq_(resp2.headers['Cache-Control'], 'no-cache')
