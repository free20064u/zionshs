from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/<int:pk>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    path('classes/', views.class_list, name='class_list'),
    path('houses/', views.house_list, name='house_list'),
    path('houses/<int:pk>/', views.house_detail, name='house_detail'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.course_create, name='course_create'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('responsibilities/', views.responsibility_list, name='responsibility_list'),
    path('responsibilities/add/', views.responsibility_create, name='responsibility_create'),
    path('responsibilities/<int:pk>/edit/', views.responsibility_edit, name='responsibility_edit'),
]
