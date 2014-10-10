#!/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from cmsplugin_contact_plus import views

urlpatterns = patterns(
    '',
    url(r'^(?P<pk>\d+)/$', views.ContactFormView.as_view(),
        name='contact_form_view'),
)
