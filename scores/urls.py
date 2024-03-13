from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('scores', views.ScoreViewSet)
router.register('students', views.StudentViewSet)
router.register('classes', views.ClassViewSet)
router.register('instructors', views.InstructorViewSet)
router.register('forums', views.ForumViewSet)
router.register('semesters', views.SemesterViewSet)
router.register('subjects', views.SemesterSubjectViewSet)
router.register('users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('forums/<int:forum_id>/comments/',
         views.CommentAPIView.as_view()),
    path('csv/', views.CSVHandleView.as_view())
]