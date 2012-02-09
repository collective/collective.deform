#!/usr/bin/python
# -*- coding: utf-8 -*-
import webob
import deform


def convertRequest(request):
    pointer = request.stdin.tell()
    try:
        request.stdin.seek(0)
        body = request.stdin.read()
        return webob.Request.blank('/', POST=body,
                                   environ=request.environ)
    finally:
        request.stdin.seek(pointer)


def translatedForm(schema, buttons, context):

    def translator(context):

        def inner_translate(msgid):
            if hasattr(msgid, 'mapping'):
                return context.translate(msgid, default=msgid.default,
                        mapping=msgid.mapping, domain=msgid.domain)
            else:
                return context.translate(msgid)

        return inner_translate

    search_path = deform.Form.default_renderer.loader.search_path
    renderer = \
        deform.template.ZPTRendererFactory(search_path=search_path,
            translator=translator(context))
    retval = deform.Form(schema, buttons=buttons, renderer=renderer,
                           css_class='enableFormTabbing deform')
    retval.widget.item_template = 'mapping_item_tabbing_compatible'
    return retval
