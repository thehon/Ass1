from django.conf.urls import url,include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from . import views

urlpatterns = [
    path('path/', views.TheView.as_view(), name="Path name")
]