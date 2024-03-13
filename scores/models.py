from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum

# Create your models here.

class Role(Enum):
    STUDENT = "STUDENT"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)
    
    def __str__(self) -> str:
        return self.value
    
class Major(Enum):
    IT = "INFORMATION TECHNOLOGY"
    CS = "COMPUTER SCIENCE"

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)
    
    def __str__(self) -> str:
        return self[1]
    
class ScoreType(Enum):
    MT = "MIDTERM"
    EOT = "END OF TERM"

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)
    
class ScoreStatus(Enum):
    ADD = "ADD"
    INPROCESS = "INPROCESS"
    UPDATED = "UPDATED"
    COMPLETE = "COMPLETE"
    DELETE = "DELETE"

    @classmethod
    def choices(cls):
        print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)

class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class User(AbstractUser):
    avatar = models.ImageField(upload_to='upload/', null=True)
    role = models.CharField(max_length=255, choices=Role.choices())
    fullname = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return self.fullname

class Instructor(BaseModel):
    major = models.CharField(max_length=255, choices=Major.choices())
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT
    )

    def __str__(self) -> str:
        return self.user.fullname

class MyClass(BaseModel):
    name = models.CharField(max_length=20, null=False, unique=True)
    major = models.CharField(max_length=100, choices=Major.choices(), null=True)

    def __str__(self) -> str:
        return self.name

class Student(BaseModel):
    myclass = models.ForeignKey(MyClass, on_delete=models.PROTECT)
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    email = models.CharField(max_length=100, null=True)
    
class Semester(BaseModel):
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self) -> str:
        return self.name

class Subject(BaseModel):
    code = models.CharField(max_length=100, null=False)
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
    
class Score(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, null=True)
    score_type = models.CharField(max_length=255, choices=ScoreType.choices())
    point = models.FloatField(null=True)
    ratio = models.FloatField(null=True)
    action = models.CharField(max_length=255, choices=ScoreStatus.choices(), default="ADD")
    note = models.CharField(max_length=255, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

class Forum(BaseModel):
    title = models.CharField(max_length=255, null=True)
    content = models.CharField(max_length=500)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_hided = models.BooleanField(default=False)

class ActionForum(BaseModel):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        unique_together = ('forum', 'user')

class Like(ActionForum):
    liked = models.BooleanField(default=True)

class Rating(ActionForum):
    rate = models.SmallIntegerField(default=0)

class Comment(BaseModel):
    content = models.CharField(max_length=255)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class SubjectTimeTable(models.Model):
    day_of_week = models.SmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)

class SemesterSubject(BaseModel):
    instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT)
    myclass = models.ForeignKey(MyClass, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT)
    # create a through model from SemesterSubject to Student
    students = models.ManyToManyField(Student, related_name='semester_subjects', blank=True)

