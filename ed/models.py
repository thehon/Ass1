from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='+', default=1)
    FirstName = models.CharField(max_length=50,default='firstname')
    LastName = models.CharField(max_length=50,default='lastname')

class Course(models.Model):
    courseCode = models.CharField(max_length=20, default="Course Code")
    courseName = models.CharField(max_length=50, default="CourseName")
    members = models.ManyToManyField(Profile, through="MemberShip", through_fields=("course", "person"))

class MemberShip(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE, null=True)
    person = models.ForeignKey(Profile,on_delete=models.CASCADE, null=True)

class Resource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    resourceName = models.CharField(max_length=50, default="Resource Name")
    resourceDescription = models.CharField(max_length=200, default="Description")
    resourceLink = models.CharField(max_length=200, default="Resource Link")

class Comment(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
