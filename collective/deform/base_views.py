#!/usr/bin/python
# -*- coding: utf-8 -*-

from Acquisition import aq_inner, aq_base
from Acquisition.interfaces import IAcquirer
from collective.colander.converter import extractFieldsFromDexterityFTI
from collective.colander.converter import extractFieldsFromDexterityObj, \
    mapZopeFieldsToColanderFields, getAllFieldSets
from collective.deform import convertRequest
from collective.deform import translatedForm
from five import grok
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from plone.memoize import instance
from Products.statusmessages.interfaces import IStatusMessage
from collective.deformwidgets.dynatree import MultiSelectDynatreeWidget, \
    DynatreeWidgetContentBrowser
from zope.component import getUtility, createObject
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
import colander
import deform
import imsvdex
from pkg_resources import resource_filename
from five.grok import PageTemplate

grok.templatedir('deform_templates')


def getVdex(context, vocab):
    stream = str(context.portal_vocabularies[vocab].getRawVdex().data)
    manager = imsvdex.vdex.VDEXManager(stream)
    return MultiSelectDynatreeWidget(vocabulary=manager)


def richtextwidget(context):
    widget = deform.widget.RichTextWidget()
    widget.strict_loading_mode = 'true'


CUSTOM_WIDGETS = {'sectors_usage_areas': lambda context: \
                  getVdex(context, 'master_category'),
                  'base_variant': lambda context: \
                  DynatreeWidgetContentBrowser(),
                  'description': richtextwidget}


def flatten_cstruct(cstruct):
    retval = {}
    for dict_ in cstruct.values():
        for (key, value) in dict_.items():
            retval[key] = value
    return retval


def unflatten_appstruct(appstruct, fieldsets):
    retval = {}
    for fieldset in fieldsets:
        subcstruct = {}
        retval[fieldset.__name__] = subcstruct
        for name in fieldset.fields:
            if name in appstruct:
                subcstruct[name] = appstruct[name]
    return retval


class DeformHelpers(grok.View):

    grok.baseclass()
    grok.template('baseform')


    @property
    @instance.memoize
    def z3c_fields(self):
        return extractFieldsFromDexterityObj(self.context)

    @property
    @instance.memoize
    def appstruct(self):
        appstruct = {}
        for field in self.z3c_fields:
            val = getattr(self.context, field.__name__, None)
            if field.__name__ in ['effective', 'expires']:
                if callable(val):
                    val = val()
            if val:
                appstruct[field.__name__] = val
        appstruct = unflatten_appstruct(appstruct, self.fieldsets)
        return appstruct

    @property
    def fieldsets(self):
        fti = getUtility(IDexterityFTI, name=self.context.portal_type)
        return getAllFieldSets(fti, self.context.portal_type)

    @property
    @instance.memoize
    def deform_form(self):
        schema = colander.SchemaNode(colander.Mapping(),
                css_class='enableFormTabbing deform')
        mapping = mapZopeFieldsToColanderFields(self.z3c_fields)
        fieldset_mapping = {}
        fieldsets = []
        unassigned_z3c_fields = [x for x in self.z3c_fields]
        for fieldset in self.fieldsets:
            hits = 0
            order_sum = 0

            fields = fieldset_mapping.get(fieldset.__name__, [])

            for field in self.z3c_fields:
                if field not in unassigned_z3c_fields:
                    continue
                if field.__name__ in fieldset.fields:
                    fields.append(field)
                    order_sum += field.order
                    hits += 1
                    unassigned_z3c_fields.remove(field)
            if fields:
                fieldset_mapping[fieldset.__name__] = fields
                if not fieldset.__name__ in [x[1] for x in fieldsets]:
                    fieldsets.append((order_sum / hits,
                            fieldset.__name__))
        fieldsets.sort()
        fieldsets = [x[1] for x in fieldsets]
        if unassigned_z3c_fields:
            fieldsets.append('others')
            fieldset_mapping['others'] = unassigned_z3c_fields

        # XXX Should be extracted

        for fieldset in fieldsets:
            subschema = colander.SchemaNode(colander.Mapping(),
                    name=fieldset)
            for field in fieldset_mapping[fieldset]:
                colander_field = mapping[field]
                if field.__name__ in CUSTOM_WIDGETS:
                    colander_field.widget = \
                        CUSTOM_WIDGETS[field.__name__](self.context)
                subschema.add(mapping[field])
            schema.add(subschema)
        schema = schema.bind(context=self.context)
        return translatedForm(schema, ('submit', 'cancel'),
                              self.context)

    def render(self):
        template_name = resource_filename("collective.deform",
            "deform_templates/baseform.pt")
        tmpl = PageTemplate(filename=template_name)
        return tmpl.render(self)


class BaseEditForm(DeformHelpers):

    grok.baseclass()

    def handleSubmit(self):
        form_data = convertRequest(self.request).POST.items()
        try:
            appstruct = \
                flatten_cstruct(self.deform_form.validate(form_data))
            for (key, value) in appstruct.items():
                setattr(self.context, key, value)
            return {'rendered_form': self.deform_form.render(self.appstruct)}
        except deform.exception.ValidationFailure, e:
            return {'rendered_form': e.render()}

    def __call__(self):
        if 'submit' in self.request.form:
            bindings = self.handleSubmit()
        else:
            bindings = \
                {'rendered_form': self.deform_form.render(self.appstruct)}
        for (key, value) in bindings.items():
            setattr(self, key, value)
        return super(BaseEditForm, self).__call__()


class BaseView(DeformHelpers):

    grok.baseclass()

    def __call__(self):
        self.rendered_form = self.deform_form.render(self.appstruct,
                readonly=True)
        return super(BaseView, self).__call__()


class BaseAddView(DeformHelpers):

    grok.baseclass()
    portal_type = 'product'

    @property
    def z3c_fields(self):
        return extractFieldsFromDexterityFTI(self.portal_type,
                self.context)

    @property
    def fieldsets(self):
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        return getAllFieldSets(fti, self.portal_type)

    def __call__(self):
        if 'submit' in self.request.form:
            bindings = self.handleSubmit()
        else:
            bindings = {'rendered_form': self.deform_form.render()}
        if not bindings:
            return None
        for (key, value) in bindings.items():
            setattr(self, key, value)
        return super(BaseAddView, self).__call__()

    def handleSubmit(self):
        form_data = convertRequest(self.request).POST.items()
        try:
            appstruct = \
                flatten_cstruct(self.deform_form.validate(form_data))
            obj = self.createAndAdd(appstruct)
            obj = self.context[obj.__name__]
            IStatusMessage(self.request).addStatusMessage(u'Item created',
                'info')
            self.request.response.redirect(obj.absolute_url())
            return None
        except deform.exception.ValidationFailure, e:
            return {'rendered_form': e.render()}

    def createAndAdd(self, data):
        obj = self.create(data)
        notify(ObjectCreatedEvent(obj))
        container = aq_inner(self.context)
        return addContentToContainer(container, obj)

    def create(self, data):
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        container = aq_inner(self.context)
        content = createObject(fti.factory)

       # Note: The factory may have done this already, but we want to be
       # sure that the created type has the right portal type. It is
       # possible to re-define a type through the web that uses the
       # factory from an existing type, but wants a unique portal_type!

        if hasattr(content, '_setPortalTypeName'):
            content._setPortalTypeName(fti.getId())

        # Acquisition wrap temporarily to satisfy things like
        # vocabularies depending on tools

        if IAcquirer.providedBy(content):
            content = content.__of__(container)
        for (key, value) in data.items():
            setattr(content, key, value)
        return aq_base(content)
