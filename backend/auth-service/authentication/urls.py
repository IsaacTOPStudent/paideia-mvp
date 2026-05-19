from django.urls import path
from .views import health_check, CustomTokenObtainPairView, logout_view
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('health/', health_check),
    path('users/', views.user_list_create, name='user-list-create'),
    path('users/<int:user_id>/', views.user_detail, name='user-detail-update'),
    path('users/<int:user_id>/activate/', views.user_reactivate, name='user-reactivate'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout')

]