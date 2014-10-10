#!/bin/env python
# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from cmsplugin_contact_plus.models import ContactPlus
from cmsplugin_contact_plus.forms import ContactFormPlus


class ContactFormView(FormMixin, DetailView):
    model = ContactPlus
    form_class = ContactFormPlus

    def get_success_url(self):
        kwargs = self.get_form_kwargs()
        try:
            return kwargs['data'][u'next']
        except KeyError:
            return super(ContactFormView, self).get_success_url()


    def get_form_kwargs(self):
        kwargs = super(ContactFormView, self).get_form_kwargs()

        kwargs['contactFormInstance'] = self.get_object()
        kwargs['request'] = self.request

        return kwargs

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(ContactFormView, self).get_context_data(**kwargs)

        form = self.get_form(self.get_form_class())
        context['form'] = form

        try:
            context['next'] = self.request.POST['next']
        except (KeyError, AttributeError):
            pass

        return context

    def form_valid(self, form):
        response = super(ContactFormView, self).form_valid(form)

        obj = self.get_object()
        email = obj.recipient_email

        form.send(email, self.request, obj)

        if self.request.is_ajax():
            return self.render_to_json_response(
                {'message': obj.thanks})
        else:
            return response



    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(ContactFormView, self).form_valid(form)

        if self.request.is_ajax():
            return self.render_to_json_response(
                form.errors, status=400)
        else:
            return response

    def post(self, request, *args , **kwargs):
        form = self.get_form(self.get_form_class())

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
