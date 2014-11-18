#!/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from inline_ordering.admin import OrderableStackedInline

from .models import ExtraField, ContactPlus


class ExtraFieldInline(OrderableStackedInline):
    model = ExtraField


class ContactFormPlusAdmin(admin.ModelAdmin):
    model = ContactPlus
    inlines = (ExtraFieldInline, )


admin.site.register(ExtraField)
admin.site.register(ContactPlus, ContactFormPlusAdmin)
