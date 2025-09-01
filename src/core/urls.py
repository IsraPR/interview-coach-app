# core/urls.py
from django.contrib import admin
from django.urls import path
from .api import api  # Root API

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
