Introduction
============

Deform is a form library that supports forms for complex structures. Unfortunately, one cannot validate complex deform forms within zope, because the request object looses the ordering of form variables. This ordering is needed by Peppercorn, which in turn is used by deform.

There is a simple fix for that, create a Webob Request object out of the raw request data. This library does exactly that.

For people not reading docs, do not forget that deform also needs some css and js files available. You are most probably using Plone, where, at least until Plone 4, js and css resource are managed by portal_javascripts and portal_css
The simplest thing to do is to just add all resources from deform there.
