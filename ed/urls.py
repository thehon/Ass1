from django.conf.urls import url,include
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('courses/', views.CourseList, name="All Courses"),
    path('courses/search', views.CourseSearch, name="Search Courses"),
    path('courses/<slug:code>', views.singleCourse, name="Course"),
    path('courses/<slug:code>/<int:id>', views.singleResource, name='Resource'),
    path('courses/<slug:code>/resource', views.addResource, name='add Resource'),
    path('courses/<slug:code>/discussion', views.discussion, name="Discussion"),
    path('', views.homeProfile, name='home'),    
    path('register', views.register, name="Register"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', views.loginView, name="login"),
    path('messages/', views.messages, name="messages"),
    path('messages/<int:id>', views.message, name="message"),      
    path('profile/', views.viewYourProfile, name="Your profile"),
    path('profile/<int:id>', views.viewProfile, name="profile"),
]