==========
bottle-api
==========


Installation
============

:: 

    $ pip install bottle-api


Basic Usage
===========

json_endpoint decorator will make a function to JSON WebAPI endpoint.
decorated function will return bottle.HTTPResponse.

see this sample web app:

::

    #!python
    from bottleapi import WebApiError
    from bottleapi.jsonapi import json_endpoint
    from bottle import Bottle, request
    
    app = Bottle()
    
    @json_endpoint
    def devide():
        a = int(request.params['a'])
        b = int(request.params['b'])
        if b == 0:
            raise WebApiError('b cannot be zero', status=400)
        
        result = a / b
        return dict(value=result)
    
    app.route('/devide', ['GET'], devide)
    

if you access ``/device?a=1&b=1``, it will return ``200 OK`` response with body:

::

    {"status": "ok", "result": {"value": 1}}

with Content-Type ``application/json``

but when you access ``device?a=1&b=0``, you will get ``400 BAD REQUEST`` response with body:

::

    {"status": "error", "message": "b cannot be zero", "result": null}


If you want to use JSONP, you can specify callback function name with parameter(``j`` by default)
So accessing ``/device?a=4&b=2&j=my_callback`` will result:

::

    my_callback({"status": "ok", "result": {"value": 2}});

If you dont like parameter or result data format, You can define your own formatters(success/error).
See jsonapi.py for customized formatter example.