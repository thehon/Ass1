from django.shortcuts import render
from django.views import generic
from .models import Course, Resource, Comment, Profile
from django.contrib.auth import authenticate, login

# Create your views here.

def CourseList(request):
    queryset = Course.objects.all()
    context = {
        'courses': queryset.all()
    }
    return render(request, 'courses.html', context=context)

def CourseSearch(request, slug):
    queryset = Course.objects.filter(courseName__icontains=slug)
    template_name = 'courses'
    context = {
        'courses': queryset.all()
    }
    return render(request, 'courses.html', context=context)

def singleCourse(request, code):
    course = Course.objects.get(courseCode=code)
    resources = Resource.objects.filter(course=course)
    context = {
        'course': course,
        'resources': resources.all()
    }
    return render(request, 'course.html', context=context)

def singleResource(request,code, id):
    resource = Resource.objects.get(id=id)
    try:
        comments = Comment.objects.get(resource=resource)
    except:
        comments = {}
    context = {
        'resource': resource,
        'comments': comments
    }
    return render(request, 'resource.html', context=context)

def homeProfile(request):    
    user = request.user
    if (not request.user.is_authenticated):
        return render(request,'login.html')
    else:
        user = Profile.objects.get(user = user)
        courses = user.courses
        print('courses: ',courses)
        context = {
            'courses': courses.all()
        }
        return render(request, 'index.html', context=context)

def loginView(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request,user)
        return (render, request, 'base.html')
    else:
        return (render, request, 'login.html')