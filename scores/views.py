from django.db import IntegrityError
from django.shortcuts import render
from django.http import Http404, HttpResponse
from rest_framework import viewsets, permissions, authentication, generics, parsers
from rest_framework.views import APIView, Response, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from .models import (
    Student, 
    Score, 
    Subject, 
    Instructor, 
    MyClass, 
    Comment, 
    Forum, 
    SemesterSubject,
    Semester,
    SubjectTimeTable,
    User,
    Like,
    Comment,
    Rating
)
from .serializers import ( 
    StudentSerializer,
    ScoreSerializer, 
    ClassSerializer, 
    InstructorSerializer, 
    SubjectSerializer, 
    ForumSerializer, 
    CommentSerializer, 
    SemesterSubjectSerializer,
    SemesterSubjectScoreSerializer,
    SemesterSerializer,
    SubjectTimeTableSerializer,
    UserSerializer
)
import csv
from io import TextIOWrapper

def index(request):
    return HttpResponse("Score Management App")

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(methods=['get'], detail=True, url_path='timetables', )
    def get_student_timetable(self, request, pk):
        student_id = request.query_params.get('student_id')
        subjects = SemesterSubject.objects.filter(semester=pk, students__in=student_id)
        timetables = SubjectTimeTable.objects.filter(semester_id=pk, subject_id__in=subjects.values_list('subject_id', flat=True))
        serializer = SubjectTimeTableSerializer(timetables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser]

    @action(methods=['get'], detail=False, url_path='user')
    def get_student_user(self, request):
        student = Student.objects.filter(email=request.query_params.get('email')).first()
        if student is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        user = student.user
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(StudentSerializer(student).data,status=status.HTTP_202_ACCEPTED)
        
    # @action(methods=['post'], detail=True, url_path='user')
    # def add_student_user(self, request, pk):
    #     student = Student.objects.get(pk=pk)
    #     user = User.objects.create(**request.data)
    #     student.user = user
    #     student.save()
    #     return Response(StudentSerializer(student).data, status=status.HTTP_200_OK)

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def filter_queryset(self, queryset):
        q = self.request.query_params.get("semester_id")
        k = self.request.query_params.get("subject_id")
        kw = self.request.query_params.get("kw")
        if q:
            queryset = queryset.filter(semester_id=q)
        if k:
            queryset = queryset.filter(subject_id=k)
        if kw: 
            queryset = queryset.filter(student=Student.objects.filter(user = User.objects.filter(fullname__contains=kw).first()).first())

        return queryset

    def create(self, request):
        l = Score.objects.create(**request.data)
        serializer = ForumSerializer(l)
        return Response(serializer.data,
            status=status.HTTP_201_CREATED)
    
    @action(methods=['post'], detail=True, url_path='complain')
    def update_score_complain(self, request, pk):
        score = Score.objects.get(pk=pk)
        score.action = 'COMPLAIN'
        score.note = request.data['note']
        score.save()
        serializer = ScoreSerializer(score)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]

class SemesterSubjectViewSet(viewsets.ModelViewSet):
    queryset = SemesterSubject.objects.all()
    serializer_class = SemesterSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def filter_queryset(self, queryset):
        q = self.request.query_params.get("semester_id")
        user = self.request.user
        if q:
            queryset = queryset.filter(semester_id=q, students__in=[user.student.id])

        return queryset

    def list(self, request, semester_id=Semester.objects.last().id):
        subjects = SemesterSubject.objects.filter(semester_id=semester_id, students__in=[request.user.student.id])
        serializer = SemesterSubjectSerializer(subjects, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False, url_path='scores')
    def get_student_scores(self, request, semester_id=1):
        subjects = SemesterSubject.objects.filter(semester_id=semester_id, students__in=[request.user.student.id])
        serializer = SemesterSubjectScoreSerializer(subjects, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ClassViewSet(viewsets.ModelViewSet):
    queryset = MyClass.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [permissions.AllowAny]

    @action(methods=['get'], detail=False, url_path='subjects')
    def get_subjects(self, request):
        semester_id = request.query_params.get("semester_id") or 1
        instructor = Instructor.objects.filter(user = request.user.id).first()
        subjects = SemesterSubject.objects.filter(instructor=instructor, semester_id=semester_id)
        return Response(SemesterSubjectSerializer(subjects, many=True, context={'request': request}).data, status=status.HTTP_200_OK)

class CommentAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    def get(self, request, forum_id):
        comments = Comment.objects.filter(forum_id=forum_id)
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data,
            status=status.HTTP_200_OK)
    def post(self, request, forum_id):
        content = request.data.get('content')
        if content is not None:
            try:
                c = Comment.objects.create(content=content,
                    user=request.user,
                    forum_id=forum_id)
            except IntegrityError:
                err_msg = "Forum does not exist!"
            else:
                return Response(CommentSerializer(c).data,
                    status=status.HTTP_201_CREATED)
        else:
            err_msg = "Content is required!!!"
            return Response(data={'error_msg': err_msg},
                status=status.HTTP_400_BAD_REQUEST)
        
class ForumPagination(PageNumberPagination):
    page_size = 6

class ForumViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.CreateAPIView, generics.ListAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    pagination_class = ForumPagination
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    def retrieve(self, request, pk):
        try:
            forum = Forum.objects.get(pk=pk)
        except Forum.DoesNotExist:
            return Http404()
        return Response(ForumSerializer(forum, context={'request': request}).data)
    def create(self, request):
        d = request.data
        l = Forum.objects.create(title=d['title'], content=d['content'], creator=request.user)
        serializer = ForumSerializer(l)
        return Response(serializer.data,
            status=status.HTTP_201_CREATED)
    
    @action(methods=['post'], detail=True, url_path='like')
    def like(self, request, pk):
        l, created = Like.objects.get_or_create(user=request.user, forum=self.get_object())
        if not created:
            l.liked = not l.liked
        l.save()

        return Response(status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=True, url_path='like')
    def like(self, request, pk):
        l = Like.objects.get(user=request.user, forum=self.get_object())
        if l is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response({"liked": l.liked}, status=status.HTTP_200_OK)


    @action(methods=['post'], detail=True, url_path='rating')
    def rating(self, request, pk):
        r, created = Rating.objects.get_or_create(user=request.user, forum=self.get_object())
        r.rate = request.data['rate']
        r.save()

        return Response(status=status.HTTP_200_OK)
    
class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['current-user', 'subjects', 'timetables']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='current-user')
    def current_user(self, request):
        return Response(UserSerializer(request.user).data)
    
    @action(methods=['get'], detail=False, url_path='timetables')
    def get_timetables(self, request):
        subjects = SemesterSubject.objects.filter(students__in=[request.user.student.id])
        timetables = SubjectTimeTable.objects.filter(subject_id__in=subjects.values_list('subject_id', flat=True))
        serializer = SubjectTimeTableSerializer(timetables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # def get(self, request):
    #     subjects = SemesterSubject.objects.all()
    #     serializer = SemesterSubjectSerializer(subjects, many=True)
    #     return Response(serializer.data,
    #         status=status.HTTP_200_OK)

class CSVHandleView(APIView):
    parser_classes = [parsers.MultiPartParser, FormParser]
    def post(self, request, *args, **kwargs):
        if 'file' in request.FILES:
            # Handling csv file before save to database
            form_data = TextIOWrapper(request.FILES['file'].file)
            csv_file = csv.reader(form_data)
            next(csv_file)  # Skip read csv header

            scores_list = []

            for line in csv_file:
                score = Score()
                score.semester_id = request.data.get("semester_id")
                score.subject_id  =request.data.get("subject_id")
                score.score_type = request.data.get("score_type")
                score.creator = request.user
                score.ratio = request.data.get("ratio")
                score.point = line[0]
                score.student_id = line[1]
                score.note = line[2]
                scores_list.append(score)

            # Save to database
            Score.objects.bulk_create(scores_list)

        return Response({
            'message': 'Import Done!'
        })
    
    def get(self, request, *args, **kwargs):
        return Response({
            'message': "Export"
        })
        # Export CSV