collective.deform
=================

collective.deform is a little helper script for using deform in zope based applications.

It does a very simple thing, it just takes the zope request object and makes a webob request object out of it.
This is probably not the most efficient way of getting deform to work with zope but is is the easiest one.

API
===

Just do the following in a view class:

>>> from collective.deform import request_converter
>>> webob_request = convert_request(self.request)
>>> my_data = my_form.validate(webob_request)

whereas my_form is supposed to be your deform form.

3 Lines is a lot of code to write, so we created a shortcut::

>>> from collective.deform import validate_form
>>> my_data = validate_form(my_form, self.request)

