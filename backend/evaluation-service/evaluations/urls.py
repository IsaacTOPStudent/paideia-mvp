from django.urls import path
from .views import health_check
from . import views

urlpatterns = [
    path('health/', health_check),
    path('evaluations/register/', views.evaluation_register, name='evaluations-register'),
    path('evaluations/', views.evaluation_list, name='evaluations-list'),
    path('evaluations/<int:evaluation_id>/', views.evaluation_detail, name='evaluations-detail'),
    path('observations/register/', views.observation_register, name='observations-register'),
    path('observations/', views.observation_list, name='observations-list'),
    path('observations/<int:observation_id>/', views.observation_detail, name='observations-detail'),
    path('longitudinal_history/<int:student_id>/', views.longitudinal_history, name='longitudinal-history')
]