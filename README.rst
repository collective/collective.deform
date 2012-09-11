Introduction
============

Deform is a form library that supports forms for complex structures. Unfortunately, one cannot validate complex deform forms within zope, because the request object looses the ordering of form variables. This ordering is needed by Peppercorn, which in turn is used by deform.

There is a simple fix for that, create a Webob Request object out of the raw request data. This library does exactly that.

API
===

Just do the following in a view class:

    >>> from collective.deform import convertRequest
    >>> webob_request = convertRequest(self.request)
    >>> my_data = my_form.validate(webob_request.POST.items())

where ``my_form`` is supposed to be your deform form.
