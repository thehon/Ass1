from django.conf.urls import url,include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('courses/', views.CourseList, name="All Courses"),
    path('courses/search/<slug:slug>', views.CourseSearch, name="Search Courses"),
    path('courses/<slug:code>', views.singleCourse, name="Course"),
    path('courses/<slug:code>/<int:id>', views.singleResource, name='Resource')   
]