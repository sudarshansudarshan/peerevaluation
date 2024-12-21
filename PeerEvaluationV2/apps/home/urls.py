# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('/add_course', views.course, name='add_course'),
    path('/add_batch', views.batch, name='add_batch'),
    path('/download_csv', views.download_csv, name='download_csv'),
    path('/enrollment', views.enrollment, name='enrollment'),
    path('ta_hub/', views.ta_hub, name='ta_hub'),

    # re_path(r'^.*\.*', views.pages, name='pages'),
]
