"""djirgha URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.views.generic import RedirectView
from djirgha.views import HotSeatView, TurnView, CurrentView

urlpatterns = [
    path("", RedirectView.as_view(url="hot-seat/"), name="index"),
    path("hot-seat/", HotSeatView.as_view(), name="hot-seat"),
    path("turn/<slug:punkt>", TurnView.as_view(), name="turn"),
    path("current/", CurrentView.as_view(), name="current"),
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
