from django.shortcuts import render
from django.views import generic
from .models import Course, Resource, Comment
# Create your views here.

def CourseList(request):
    queryset = Course.objects.all()
    template_name = 'courses'
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
    #comments = Comment.objects.get(resource=resource)
    context = {
        'resource': resource,
        
    }
    return render(request, 'resource.html', context=context)