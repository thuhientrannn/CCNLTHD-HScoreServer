from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import (
    Instructor, 
    MyClass, 
    Student, 
    Subject, 
    Score, 
    User, 
    Comment, 
    Forum, 
    SemesterSubject, 
    Semester, 
    Major,
    SubjectTimeTable
)
from django.forms.models import model_to_dict
import json


def get_avatar(self, obj):
    if obj.avatar:
        request = self.context.get('request')
        if request is not None:
            if obj.avatar.name.startswith('static/'):
                path = "/%s" % obj.avatar.name
            else:
                path = '/static/%s' % (obj.avatar)
            return request.build_absolute_uri(path)

class SemesterSerializer(ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'name', 'start_time', 'end_time']
        
class UserSerializer(ModelSerializer):
    avatar = SerializerMethodField(source='image')

    def get_avatar(self, obj):
        return get_avatar(self, obj)
    
    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(u.password)
        u.save()
        return u

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'fullname', 'role', 'is_active', 'avatar']

class InstructorSerializer(ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Instructor
        fields = ['major', 'user']

class ClassSerializer(ModelSerializer):
    class Meta:
        model = MyClass
        fields = ['name', 'major']

class StudentSerializer(ModelSerializer):
    myclass = ClassSerializer()
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['id','myclass', 'user']


class SubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id','code', 'name' ,'description', 'active']

class SemesterSubjectSerializer(ModelSerializer):
    subject = SubjectSerializer()
    instructor = InstructorSerializer()
    myclass = ClassSerializer()

    class Meta:
        model = SemesterSubject
        fields = ['subject', 'semester', 'instructor', 'myclass', 'start_time', 'end_time', 'active']


class SemesterSubjectScoreSerializer(ModelSerializer):
    scores = SerializerMethodField()
    subject = SubjectSerializer()
    instructor = InstructorSerializer()
    myclass = ClassSerializer()
    def get_scores(self, obj):
        request = self.context.get('request')
        scores = Score.objects.filter(subject=obj.subject, semester = obj.semester, student = request.user.student)
        serializer = ScoreSerializer(scores, many=True)
        return serializer.data
    
    class Meta:
        model = SemesterSubjectSerializer.Meta.model
        fields = ['subject', 'semester', 'instructor', 'myclass', 'start_time', 'end_time', 'active', 'scores']
        

class SubjectTimeTableSerializer(ModelSerializer):
    subject = SubjectSerializer()
    class Meta:
        model = SubjectTimeTable
        fields = ['subject','day_of_week', 'start_time', 'end_time']

class ScoreSerializer(ModelSerializer):
    student = StudentSerializer()
    class Meta:
        model = Score
        fields = ['id', 'point', 'score_type', 'ratio', 'updated_date', 'action', 'note', 'student']

class ForumSerializer(ModelSerializer):
    creator = UserSerializer()
    likes = SerializerMethodField()
    comments = SerializerMethodField()

    def get_likes(self, obj):
        return obj.like_set.count()
    
    def get_comments(self, obj):
        return obj.comment_set.count()

    class Meta:
        model = Forum
        fields = ['id', 'title', 'content', 'creator', 'created_date', 'updated_date', 'likes', 'comments']

class CommentSerializer(ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Comment
        fields = ['user', 'content', 'created_date']

class MajorSerializer(ModelSerializer):
    class Meta:
        model = Major
        fields = ['major']


