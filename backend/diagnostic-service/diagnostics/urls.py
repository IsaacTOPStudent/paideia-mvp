from django.urls import path
from .views import health_check
from . import views

urlpatterns = [
    path('health/', health_check),
    path('diagnostic/catalog/', views.create_diagnostic, name='create-diagnostic'),
    path('diagnostics/catalog/', views.list_diagnostics, name='list-diagnostics'),
    path('diagnostics/catalog/<int:diagnostic_id>/', views.update_diagnostic, name='update-diagnostic'),
    path('diagnostics/catalog/<int:diagnostic_id>/deactivate/', views.deactivate_diagnostic, name='deactivate-diagnostic'),
    path('diagnostics/characterizations/', views.characterize_student, name='characterize-student'),
    path('diagnostics/student/<int:student_id>/characterizations/', views.characterizations_by_student, name='characterizations-student')
    
]

