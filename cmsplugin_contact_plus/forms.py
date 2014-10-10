#!/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import forms
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from slugify import slugify
from django.conf import settings

from cmsplugin_contact_plus.models import ContactPlus

from cmsplugin_contact_plus.signals import *


class ContactFormPlus(forms.Form):

    def __init__(self, contactFormInstance, request, *args, **kwargs):
        super(ContactFormPlus, self).__init__(*args, **kwargs)

        if 'instance' not in kwargs:
            for extraField in contactFormInstance.extrafield_set.all():
                label = slugify(extraField.label)
                field = None

                if extraField.fieldType == 'CharField':
                    field = forms.CharField(
                        label=extraField.label,
                        initial=extraField.initial,
                        required=extraField.required)
                elif extraField.fieldType == 'BooleanField':
                    field = forms.BooleanField(
                        label=extraField.label,
                        initial=extraField.initial,
                        required=extraField.required)
                elif extraField.fieldType == 'EmailField':
                    field = forms.EmailField(
                        label=extraField.label,
                        initial=extraField.initial,
                        required=extraField.required)
                elif extraField.fieldType == 'DecimalField':
                    field = forms.DecimalField(
                        label=extraField.label,
                        initial=extraField.initial,
                        required=extraField.required)
                elif extraField.fieldType == 'FloatField':
                    field = forms.FloatField(
                        label=extraField.label,
                        initial=extraField.initial,
                        required=extraField.required)
                elif extraField.fieldType == 'IntegerField':
                    field = forms.IntegerField(
                        label=extraField.label,
                        initial=extraField.initial,
                        required=extraField.required)
                elif extraField.fieldType == 'IPAddressField':
                    field = forms.IPAddressField(
                        label=extraField.label,
                        initial=extraField.initial,
                        required=extraField.required)
                elif extraField.fieldType == 'auto_Textarea':
                    field = forms.CharField(
                        label=extraField.label,
                        initial=extraField.initial,
                        widget=forms.Textarea,
                        required=extraField.required)
                elif extraField.fieldType == 'auto_hidden_input':
                    field = forms.CharField(
                        label=extraField.label,
                        initial=extraField.initial,
                        widget=forms.HiddenInput,
                        required=False)
                elif extraField.fieldType == 'auto_referral_page':
                    lInitial = "No referral available."
                    if request:
                        lInitial = request.META.get(
                            'HTTP_REFERER', 'No referral available.')
                    field = forms.CharField(
                        label=extraField.label,
                        # NOTE: This overwrites extraField.initial!
                        initial=lInitial,
                        widget=forms.HiddenInput,
                        required=False)
                elif extraField.fieldType == 'auto_GET_parameter':
                    lInitial = "Key/value parameter not available."

                    if request:
                        lInitial = request.GET.get(label, 'n/a')

                    field = forms.CharField(
                        label=extraField.label,
                        # NOTE: This overwrites extraField.initial!
                        initial=lInitial,
                        widget=forms.HiddenInput,
                        required=False)

                self.fields[slugify(extraField.label)] = field

    def send(self, recipient_email, request, instance=None):
        current_site = Site.objects.get_current()
        if instance:
            order = ContactPlus.objects.get(
                id=instance.id).extrafield_set.order_by(
                    'inline_ordering_position')

            ordered_dic_list = []

            for field in order:
                key = slugify(field.label)
                value = self.cleaned_data.get(key, '(no input)')
                ordered_dic_list.append({field.label: value})

            # self.cleaned_data = None

        email_message = EmailMessage(
            "[" + current_site.domain.upper() + "]",
            render_to_string("cmsplugin_contact_plus/email.txt", {
                'data': self.cleaned_data,
                'ordered_data': ordered_dic_list,
                'instance': instance,
            }),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            to=[recipient_email, ],
            headers={
                #TODO: use settings to define the label.
                # 'Reply-To': self.cleaned_data['email']
            },)

        email_message.send(fail_silently=True)
        contact_message_sent.send(sender=self, data=self.cleaned_data)
