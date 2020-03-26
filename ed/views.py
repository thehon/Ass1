from django.shortcuts import render
from django.views import generic
from .models import Course, Resource, Comment, Profile, MemberShip
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
# Create your views here.

def CourseList(request):
    queryset = Course.objects.all()
    context = {
        'courses': queryset.all()
    }
    return render(request, 'courses.html', context=context)

def CourseSearch(request):
    slug = request.POST['search']
    
    try:
        queryset = Course.objects.filter(courseName__icontains=slug)
        print('queryset: ', queryset)
        courses = queryset.all()
    except:
        queryset = {}
        courses = {}    
    context = {
        'courses': courses,
        'slug': slug
    }
    return render(request, 'courses.html', context=context)

def singleCourse(request, code):
    if not request.POST:
        try: 
            course = Course.objects.get(courseCode=code)
        except:
            course = None
        try:
            resources = Resource.objects.filter(course=course)
            resources = resources.all()
        except:
            resources = None
        #Try and see if you are subscribed to this course
        try:
            userProfile = Profile.objects.get(user=request.user)
            exist = MemberShip.objects.filter(person=userProfile, course=course)
            if exist:
                subscribed = True
            else:
                subscribed = False
        except: 
            subscribed = False
        context = {
            'course': course,
            'resources': resources,
            'subscribed': subscribed,            
        }
        return render(request, 'course.html', context=context)
    else:
        subscribed = False
        try:
            course = Course.objects.get(courseCode=code)
        except:
            course = None
        userProfile = Profile.objects.get(user=request.user)
        #userProfile.courses.add(course)
        exist = MemberShip.objects.filter(person=userProfile, course=course)
        if exist:
            exist.delete()
            
        else:
            m = MemberShip(person=userProfile, course=course)
            m.save()
            subscribed = True
        try:
            resources = Resource.objects.filter(course=course)
            resources = resources.all()
        except:
            resources = None
        context = {
            'course': course,
            'resources' : resources,
            'subscribed': subscribed
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
        courses = MemberShip.objects.filter(person=user)
        courses = courses.values_list('course', flat=True)
        courseItems = Course.objects.filter(id__in=courses)
        context = {
            'courses': courseItems.all()
        }
        return render(request, 'index.html', context=context)

def loginView(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request,user)
        return render(request, 'base.html')
    else:
        return render(request, 'index.html')

def register(request):
    if request.POST:
        username = request.POST['username']
        firstName = request.POST['firstname']
        lastName = request.POST['lastname']    
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username, email, password)
        P = Profile(user=user, FirstName=firstName, LastName=lastName)
        P.save()
        return render(request, 'index.html')
    else:
        return render(request, 'register.html')

