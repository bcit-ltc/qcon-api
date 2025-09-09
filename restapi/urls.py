# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.urls import include, path, re_path
from . import views
from django.conf import settings

urlpatterns = [
    path('format', views.format),
    path('sections', views.sections),
    path('splitter', views.splitter),
    path('parsequestion', views.parsequestion)
]

