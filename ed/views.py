from django.shortcuts import render
from django.views import generic
from .models import Course, Resource, Comment, Profile, MemberShip, ChatMembership, Message, Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Q
# Create your views here.

def CourseList(request):
    queryset = Course.objects.all()
    context = {
        'active': 'courses',
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
        'active': 'courses',
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
        members = MemberShip.objects.filter(course=course)
        profileIds = members.values_list('person', flat=True)
        profiles = Profile.objects.filter(id__in=profileIds)
        context = {
            'course': course,
            'active': 'courses',
            'resources': resources,
            'subscribed': subscribed,
            'profiles': profiles            
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
            'active': 'courses',
            'resources' : resources,
            'subscribed': subscribed
        }
        return render(request, 'course.html', context=context)

def singleResource(request,code, id):    
    if not request.POST:
        resource = Resource.objects.get(id=id)
        try:
            comments = Comment.objects.filter(resource=resource)
        except:
            comments = {}
        context = {
            'active': 'courses',
            'resource': resource,
            'comments': comments
        }
        return render(request, 'resource.html', context=context)
    else:
        user = request.user
        body = request.POST['comment']
        resource = request.POST['resource']
        resourceObject = Resource.objects.get(id=resource)
        profile = Profile.objects.get(user=user)
        c = Comment(resource=resourceObject, body=body, user=profile)
        c.save()

        comments = Comment.objects.filter   (resource=resource)
        context = {
            'active': 'courses',
            'resource': resourceObject,
            'comments': comments.all()
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
            'active': 'home',
            'courses': courseItems.all()
        }
        return render(request, 'index.html', context=context)

def loginView(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request,user)
        return render(request, 'index.html')
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

def addResource(request, code):
    resourcename = request.POST['resourcename']
    resourcedesc = request.POST['resourcedesc']
    resourcelink = request.POST['resourcelink']
    code = request.POST['coursecode']
    course = Course.objects.get(courseCode=code)

    r = Resource(course=course, resourceName=resourcename, resourceDescription=resourcedesc, resourceLink=resourcelink)
    r.save()

    return render(request, 'index.html')

def messages(request):
    #get all my messages
    profile = Profile.objects.get(user=request.user)
    chatmemberships = ChatMembership.objects.filter(person=profile)
    chatmemberships = chatmemberships.values_list('group', flat=True)

    groups = Group.objects.filter(id__in=chatmemberships)
    #groups = groups profile is apart of
    members = groups.values_list('members', flat=True)    
    ps = Profile.objects.filter(id__in=members)

    context = {
        'active': 'messages',
        'members': ps.all()
    }
    return render(request, 'messages.html', context=context)

def message(request,id):
    profile = Profile.objects.get(user=request.user)
    otherID = Profile.objects.get(id=id)
    chat = Group.objects.filter(members=profile.id)

    memberships1 = ChatMembership.objects.filter(person=profile.id)
    memberships2 = ChatMembership.objects.filter(person=id)

    groups1 = memberships1.values_list('group', flat=True)
    groups2 = memberships2.values_list('group', flat=True)

    group = list(set(groups1).intersection(groups2))
    print("Group: ", group)
    if group:
        #the chat already exists
        group = Group.objects.get(id=group[0])
    else:
        #the chat doesnt exist - need to create 1 (empty)
        g = Group()
        g.save()
        membership1 = ChatMembership(person=profile, group=g)
        membership2 = ChatMembership(person=otherID, group=g)
        membership1.save()
        membership2.save()
        group = g


    #chat = chat.get(members=id)
    if not request.POST:
        messages = group.messages.all()
        msg = Message.objects.filter(id__in=messages)
        context= {
            'id': id,
            'active': 'messages',
            'messages' : msg
        }
        return render(request, 'message.html', context=context)
    else:
        #it is a post
        sender = Profile.objects.get(user=request.user)
        m = Message(sender=sender, body=request.POST['message'])
        m.save()
        group.messages.add(m)
        group.save()
        messages = group.messages.all()
        msg = Message.objects.filter(id__in=messages)
        context= {
            'id': id,
            'active': 'messages',
            'messages' : msg
        }
        return render(request, 'message.html', context=context)
    
def viewYourProfile(request):
    p = Profile.objects.get(user=request.user)
    courses = MemberShip.objects.filter(person=p)
    courses = courses.values_list('course', flat=True)
    courseItems = Course.objects.filter(id__in=courses)
    context = {
        'self': True,
        'active': 'profile',
        'profile': p,
        'courses': courseItems.all()
    }
    return render(request, 'profile.html', context=context)

def viewProfile(request, id):
    p1 = Profile.objects.get(user=request.user)

    p = Profile.objects.get(id=id)
    if p == p1:
        isself = True
    else:
        isself = False

    courses = MemberShip.objects.filter(person=p)
    courses = courses.values_list('course', flat=True)
    courseItems = Course.objects.filter(id__in=courses)
    context = {
        'self': isself,
        'profile': p,
        'courses': courseItems.all()
    }
    return render(request, 'profile.html', context=context)