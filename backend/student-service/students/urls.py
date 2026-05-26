from django.urls import path
from .views import health_check
from . import views

urlpatterns = [
    path('health/', health_check),
    path('students/register/', views.student_register, name='student-register'),
    path('students/', views.student_list, name='student-list'),
    path('students/<int:student_id>/', views.student_detail, name='student-detail'),
    path('students/<int:student_id>/update/', views.update_student, name='update-student'),
    path('students/<int:student_id>/deactivate/', views.deactivate_student, name='deactivate-student')
]