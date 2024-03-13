from django import forms
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from .models import (
    Instructor, 
    Student, 
    MyClass, 
    Subject, 
    Score, 
    Forum, 
    Comment, 
    SemesterSubject, 
    User,
    Semester,
    SubjectTimeTable
)

# Register your models here.

class ScoreAppAdminSite(admin.AdminSite):
    site_header = 'Hệ thống quản lý điểm'

    def get_urls(self):
        return [
            path('course-stats/', self.stats_view),
        ] + super().get_urls()
    
    def stats_view(self, request):
        pass

admin_site = ScoreAppAdminSite(name='myadmin')

@admin.display(description="Class")
def myclass(obj):
    return obj.myclass.name + " - " + obj.myclass.major

class SemesterAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time']

class InstructorAdmin(admin.ModelAdmin):
    list_display = ['major']

class StudentAdmin(admin.ModelAdmin):
    list_display = [myclass]

class MyClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'major']

class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

class ScoreAdmin(admin.ModelAdmin):
    list_display = ['point', 'subject', 'student']

class CommentInlineAdmin(admin.StackedInline):
    model = Comment
    fk_name = 'forum'

class ForumAdmin(admin.ModelAdmin):
    list_display = ['content', 'creator', 'is_hided']
    inlines = [CommentInlineAdmin,]

class SemesterSubjectAdmin(admin.ModelAdmin):
    list_display = ['subject', 'semester', 'instructor', 'myclass', 'start_time', 'end_time']

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'fullname', 'role']

class SubjectTimeTableAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'start_time', 'end_time']

admin_site.register(Instructor, InstructorAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(MyClass, MyClassAdmin)
admin_site.register(Subject, SubjectAdmin)
admin_site.register(Score, ScoreAdmin)
admin_site.register(Forum, ForumAdmin)
admin_site.register(SemesterSubject, SemesterSubjectAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(Semester, SemesterAdmin)
admin_site.register(SubjectTimeTable, SubjectTimeTableAdmin)