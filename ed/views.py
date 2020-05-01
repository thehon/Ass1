from django.shortcuts import render
from django.views import generic
from .models import Course, Resource, Comment, Profile, MemberShip, ChatMembership, Message, Group, Discussion
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q,F,Sum
from .waf import cleanStrings, get_client_ip, get_waf_entries
import requests
from helpers import PasswordRules
# Create your views here.

def CourseList(request):
    queryset = Course.objects.all()
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True  
    context = {
        'active': 'courses',
        'courses': queryset.all(),
        'is_admin': is_admin
    }
    return render(request, 'courses.html', context=context)

def CourseSearch(request):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True  
    slug = request.POST['search']
    cleanedDic = cleanStrings('search', '/course', {'slug':slug}, str(request.user.username))
    slug = cleanedDic['slug']
    try:
        queryset = Course.objects.filter(Q(courseName__icontains=slug) | Q(courseCode__icontains=slug))        
        courses = queryset.all()
    except:
        queryset = {}
        courses = {}    
    context = {
        'active': 'courses',
        'courses': courses,
        'slug': slug,
        'is_admin': is_admin
    }
    return render(request, 'courses.html', context=context)

def singleCourse(request, code):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True
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
        discussions = Discussion.objects.filter(course=course)
        context = {
            'course': course,
            'active': 'courses',
            'resources': resources,
            'subscribed': subscribed,
            'profiles': profiles.all(),
            'discussions': discussions.all(),
            'is_admin': is_admin            
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
        members = MemberShip.objects.filter(course=course)
        profileIds = members.values_list('person', flat=True)
        profiles = Profile.objects.filter(id__in=profileIds)
        discussions = Discussion.objects.filter(course=course)
        context = {
            'course': course,
            'active': 'courses',
            'resources' : resources,
            'subscribed': subscribed,
            'profiles': profiles.all(),
            'discussions': discussions.all(),
            'is_admin': is_admin
        }
        return render(request, 'course.html', context=context)

def singleResource(request,code, id):   
    is_admin = False
    p = Profile.objects.get(user=request.user)
    error = ''
    if p.is_admin:
        is_admin = True  
    if not request.POST:
        resource = Resource.objects.get(id=id)
        try:
            comments = Comment.objects.filter(resource=resource).\
                annotate(totalvotes = F('upvotes') - F('downvotes')).order_by('-totalvotes')
        except:
            comments = {}
        context = {
            'active': 'courses',
            'resource': resource,
            'comments': comments,
            'is_admin': is_admin
        }
        return render(request, 'resource.html', context=context)
    else:
        #could be upvote or downvote
        votetype = request.POST.get('votetype', False)
        user = request.user
        profile = Profile.objects.get(user=user)          
        if votetype:
            comment = Comment.objects.get(id=request.POST['commentID'])
            if votetype == 'downvote':
                comment.downvotes = comment.downvotes + 1
            else:
                comment.upvotes = comment.upvotes + 1
            comment.save()
            resource = id
        else:
            body = request.POST.get('comment', False)
            cleanedDic = cleanStrings('comment', '/course' + code, {'comment': body}, str(request.user.username))
            if cleanedDic:
                body = cleanedDic['comment']
            if not body:
                error = 'Please enter a comment'                    
            resource = request.POST.get("resource", False)
            if not resource:
                error = 'Please enter a Link'                    
            if body and resource:
                resourceObject = Resource.objects.get(id=resource)
                c = Comment(resource=resourceObject, body=body, user=profile)
                c.save()
        
        resourceObject = Resource.objects.get(id=resource)
          
        comments = Comment.objects.filter(resource=resource).\
                annotate(totalvotes = F('upvotes') - F('downvotes')).order_by('totalvotes')
        context = {
            'active': 'courses',
            'resource': resourceObject,
            'comments': comments.all(),
            'is_admin': is_admin,
            'error': error
        }
        return render(request, 'resource.html', context=context)


def homeProfile(request):
    is_admin = False
    if not request.user.is_authenticated:
        context= {
            'active': 'login'
        }
        return render(request,'login.html', context=context)
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True      
    user = request.user
    if (not request.user.is_authenticated):
        context= {
            'active': 'login'
        }
        return render(request,'login.html', context=context)
    else:
        user = Profile.objects.get(user = user)
        courses = MemberShip.objects.filter(person=user)
        courses = courses.values_list('course', flat=True)
        courseItems = Course.objects.filter(id__in=courses)
        context = {
            'active': 'home',
            'courses': courseItems.all(),
            'is_admin': is_admin
        }
        return render(request, 'index.html', context=context)

def loginView(request):
    username = request.POST.get('username',False)
    password = request.POST.get('password',False)
    error = ''
    if not username:
        error = 'Please enter a username'
        context = {'error': error, 'active': 'login'}
        return render(request, 'login.html', context=context)
    if not password: 
        error = error + "Please enter a password"
        context = {'error': error, 'active': 'login'}
        return render(request, 'login.html', context=context)
    cleanedDic = cleanStrings('login', 'login', {'username': username, 'password': password, 'ip':get_client_ip(request)})
    if cleanedDic:
        username = cleanedDic['username']
        password = cleanedDic['password']
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request,user)
        p = Profile.objects.get(user = user)
        if p.is_admin:
            is_admin = True
        else:
            is_admin = False
        courses = MemberShip.objects.filter(person=p)
        courses = courses.values_list('course', flat=True)
        courseItems = Course.objects.filter(id__in=courses)
        context = {
            'active': 'home',
            'courses': courseItems.all(),
            'is_admin': is_admin
        }
        return render(request, 'index.html', context=context)
    else:
        error = "Invalid login details"
        context = {
            'active': 'login',
            'error': error
        }
        return render(request, 'login.html', context=context)

def register(request):
    if request.POST:
        username = request.POST.get('username',False)
        error = ""
        if not username:
            error = 'Please enter a username'
            context = { 'error': error, 'active': 'register'}
            return render(request, 'register.html', context=context)    

        firstName = request.POST.get('firstname',False)
        if not firstName:
            error = 'Please enter a username'
        
        lastName = request.POST.get('lastname', False)
        if not lastName:
            error = 'please enter a lastname'    
        
        email = request.POST.get('email', False)
        if not email:
            error = 'please enter an email'
            
        context = {}
        password = request.POST.get('password',False)
        if not password:
            error = 'please enter a password'
        
        if error != "":
            context = { 'error': error, 'active': 'register'}
            return render(request, 'register.html', context=context)
        try:
            cleanedDic = cleanStrings('register', '/register', {'username': username, 'password':password, 'firstname':firstName, 'lastname':lastName, 'email':email, 'ip': get_client_ip(request)})
            print('cleanedDic: ', cleanedDic)
            if cleanedDic:
                username = cleanedDic['username']
                password = cleanedDic['password']
                email = cleanedDic['email']
                firstName = cleanedDic['firstname']
                lastName = cleanedDic['lastname']            
            error, approved = PasswordRules(password)
            if not approved:
                context = { 'error': error}
                return render(request, 'register.html',context=context)
            user = User.objects.create_user(username, email, password)
            P = Profile(user=user, FirstName=firstName, LastName=lastName, is_admin=False)
            P.save()
            login(request, user)     
        
            
        except Exception as e:
            print('register exception: ', e)
            if e.__class__.__name__ == 'IntegrityError':
                error = 'This username is taken - please select a different one'
                context = { 'error': error}
            else:
                print(e)
                context = { 'error': e.__class__.__name__}
            return render(request, 'register.html', context=context)
        return render(request, 'index.html')
    else:
        return render(request, 'register.html')

def addResource(request, code):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True
    error = ''
    resourcename = request.POST.get('resourcename', False)
    if not resourcename:
        error = 'Please enter a name'
    
    resourcedesc = request.POST.get('resourcedesc',False)
    if not resourcedesc:
        error = 'Please enter a description'
    
    resourcelink = request.POST.get('resourcelink','')
    
    code = request.POST['coursecode']
    
    course = Course.objects.get(courseCode=code)
    if resourcename and resourcedesc:
        r = Resource(course=course, resourceName=resourcename, resourceDescription=resourcedesc, resourceLink=resourcelink)
        r.save()
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
    discussions = Discussion.objects.filter(course=course)
    try:
        resources = Resource.objects.filter(course=course)
        resources = resources.all()
    except:
        resources = None
    context = {
        'course': course,
        'active': 'courses',
        'resources': resources,
        'subscribed': subscribed,
        'profiles': profiles,
        'discussions': discussions.all(),
        'is_admin': is_admin,
        'error': error           
    }        
    return render(request, 'course.html', context=context)

def messages(request):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True  
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
        'members': ps.all(),
        'is_admin': is_admin
    }
    return render(request, 'messages.html', context=context)

def message(request,id):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True  
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
        msg = Message.objects.filter(id__in=messages).order_by('-id')

        context= {
            'id': id,
            'active': 'messages',
            'messages' : msg,
            'is_admin': is_admin,
            'otherID': otherID
        }
        return render(request, 'message.html', context=context)
    else:
        #it is a post
        sender = Profile.objects.get(user=request.user)
        messageBody = request.POST.get("message", False)
        error = ""
        if not messageBody or messageBody == ' ':
            error = 'Enter a message to send'
        else:
            cleanedMessage = cleanStrings('message', '/message', {'messageBody': messageBody}, str(request.user.username))
            if cleanedMessage:
                messageBody = cleanedMessage['messageBody']
            m = Message(sender=sender, body=messageBody)
            m.save()
            group.messages.add(m)
            group.save()
        messages = group.messages.all()
        msg = Message.objects.filter(id__in=messages)
        context= {
            'id': id,
            'active': 'messages',
            'messages' : msg,
            'is_admin': is_admin,
            'otherID': otherID,
            'error': error            
        }
        return render(request, 'message.html', context=context)
    
def viewYourProfile(request):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True  
    p = Profile.objects.get(user=request.user)
    courses = MemberShip.objects.filter(person=p)
    courses = courses.values_list('course', flat=True)
    courseItems = Course.objects.filter(id__in=courses)
    context = {
        'self': True,
        'active': 'profile',
        'profile': p,
        'courses': courseItems.all(),
        'is_admin': is_admin
    }
    return render(request, 'profile.html', context=context)

def viewProfile(request, id):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True  
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
        'courses': courseItems.all(),
        'is_admin': is_admin
    }
    return render(request, 'profile.html', context=context)

def discussion(request,code):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True  
    if request.POST:
        p = Profile.objects.get(user=request.user)
        course = Course.objects.get(courseCode=code)
        discussion = request.POST.get('discussionbody', False)
        error = ''
        cleanedDic = cleanStrings('comment', '/' + course.courseCode, {'comment': discussion}, str(request.user.username))
        if cleanedDic:
            discussion = cleanedDic['comment']
        if discussion != False:
            d = Discussion(course=course, sender=p,body=discussion)
            d.save()
        else:
            error = "Please enter discussion content"
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
        discussions = Discussion.objects.filter(course=course)
        context = {
            'course': course,
            'active': 'courses',
            'resources': resources,
            'subscribed': subscribed,
            'profiles': profiles,
            'discussions': discussions.all(),
            'is_admin': is_admin,
            'error': error                    
        }
        return render(request, 'course.html', context=context)

def admin(request, id):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        if request.POST:
            profiles = Profile.objects.all()
            profiles = profiles.all()
            postType = request.POST['postType']
            if postType == 'addAdmin':
                #only change admin status if user is admin
                otherUser = Profile.objects.get(id=id)
                otherUser.is_admin = not otherUser.is_admin
                otherUser.save()
                is_admin = True
                profiles = Profile.objects.all()
                context = {
                    'is_admin': is_admin,
                    'profiles': profiles 
                }
                return render(request, 'admin.html', context=context)
            if postType == 'removeCourse':
                course = Course.objects.get(id=id)
                if course:
                    course.delete()
                return render(request, 'admin.html')
            if postType =='addCourse':
                
                c = Course()
                coursecode = request.POST.get('courseCode', False)
                error = ''
                if not coursecode:
                    error = 'please enter a coursename'
                coursename = request.POST.get('courseName', False)
                if not coursename:
                    error = 'please enter a course code'
                if coursename and coursecode:
                    cleanedDic = cleanStrings('addcourse', '/admin', {'coursename': coursename, 'coursecode':coursecode}, str(request.user.username))
                    if cleanedDic:
                        coursename = cleanedDic['coursename']
                        coursecode = cleanedDic['coursecode']
                    c.courseName = coursename
                    c.courseCode = coursecode    
                    c.save()
                context = {
                    'error': error,
                    'profiles': profiles
                }
                return render(request, 'admin.html',context=context)
            if postType == 'removeDiscussion':
                d = Discussion.objects.get(id=id)
                if d:
                    d.delete()
                return render(request, 'admin.html')
            if postType == 'removeComment':
                c = Comment.objects.get(id=id)
                if c:
                    c.delete()
                return render(request, 'admin.html')
            if postType == 'removeResource':
                r = Resource.objects.get(id=id)
                if r:
                    r.delete()
                return render(request, 'admin.html')


    else:
        return render(request, 'index.html')

def adminPage(request):
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        profiles = Profile.objects.all()
        entries = get_waf_entries()
        if entries:
            entries = entries['entries']
        else:
            entries = {}
        print(entries)
        context = {
            'active': 'admin',
            'is_admin': True,
            'profiles': profiles,
            'wafs': entries
        }
        return render(request, 'admin.html', context=context)
    else:
        return render(request, 'index.html')

def addme(request):
    p = Profile.objects.get(user=request.user)
    p.is_admin = True
    p.save()
    profiles = Profile.objects.all()
    context = {
            'is_admin': True,
            'profiles': profiles
        }
    return render(request,'admin.html', context=context)

def userLogout(request):
    user = request.user
    logout(request)
    return render(request, 'login.html')

def handleVote(request, id):
    if request.POST:
        votetype = request.POST['votetype']
        comment = Comment.objects.get(id=request.POST['commentID'])
        if votetype == 'downvote':
            comment.downvote = comment.downvote + 1
        else:
            comment.upvote = comment.upvote + 1
    resource = Resource.objects.get(id=id)
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True
    try:
        comments = Comment.objects.filter(resource=resource)
    except:
        comments = {}
    context = {
        'active': 'courses',
        'resource': resource,
        'comments': comments,
        'is_admin': is_admin
    }
    return render(request, 'resource.html', context=context)

def userDelete(request,id):
    user = Profile.objects.get(user=request.user)
    is_admin = False
    message = ''
    if user:
        if user.is_admin:
            is_admin = True
            todelete = Profile.objects.get(id=id)
            if todelete:
                todelete.delete()
                message = 'You have succesfully deleted ' + todelete.FirstName + " " +todelete.LastName + "'s account"
    courses = MemberShip.objects.filter(person=user)
    courses = courses.values_list('course', flat=True)
    courseItems = Course.objects.filter(id__in=courses)
    context = {
        'active': 'home',
        'courses': courseItems.all(),
        'is_admin': is_admin,
        'message': message
    }
    
    return render(request, 'index.html', context=context)            

def searchProfiles(request):
    user = Profile.objects.get(user=request.user)
    is_admin = False
    if user.is_admin:
        is_admin = True
    name = request.POST.get('search', False)
    error = ''
    if name != "":
        profiles = Profile.objects.filter(Q(FirstName__icontains=name) | Q(LastName__icontains=name)).exclude(id=user.id)
        profiles = profiles.all()
    else:
        profiles=[]
        error = 'Please enter a name to search'

    context = {
        'is_admin': True,
        'active' : 'messages',
        'profiles': profiles,
        'error': error
    }
    return render(request, 'messages.html', context=context)

def deleteDiscussion(request,id,code):
    is_admin = False
    p = Profile.objects.get(user=request.user)
    if p.is_admin:
        is_admin = True  
    discussionComment = Discussion.objects.get(id=id)
    course = Course.objects.get(id=discussionComment.course.id)
    if discussionComment:
        discussionComment.delete()
    userProfile = Profile.objects.get(user=request.user)
    exist = MemberShip.objects.filter(person=userProfile, course=course)
    if exist:
        subscribed = True
    else:
        subscribed = False
    members = MemberShip.objects.filter(course=course)
    profileIds = members.values_list('person', flat=True)
    profiles = Profile.objects.filter(id__in=profileIds)
    discussions = Discussion.objects.filter(course=course)
    context = {
        'course': course,
        'active': 'courses',
        'subscribed': subscribed,
        'discussions': discussions.all(),
        'is_admin': is_admin,        
    }
    return render(request, 'course.html', context=context)        

def changeProfile(request):
    
    p = Profile.objects.get(user=request.user)
    is_admin = False
    if p.is_admin:
        is_admin = True 
        
    firstname = request.POST.get('firstname', False)
    lastname = request.POST.get('lastname', False)
    cleanedDic = cleanStrings('changeprofile', '/profile', { 'lastname': lastname, 'firstname': firstname}, str(request.user.username))
    if cleanedDic:
        firstname = cleanedDic['firstname']
        lastname = cleanedDic['lastname']
    if firstname:
        p.FirstName = firstname
    if lastname:
        p.LastName = lastname
    
    p.save()
    isself = True    
    courses = MemberShip.objects.filter(person=p)
    courses = courses.values_list('course', flat=True)
    courseItems = Course.objects.filter(id__in=courses)
    context = {
        'self': isself,
        'profile': p,
        'courses': courseItems.all(),
        'is_admin': is_admin
    }
    return render(request, 'profile.html', context=context)
