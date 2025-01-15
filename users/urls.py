from django.urls import path
from .views import (
    UserRegistrationAPIView,
    activate,
    UserLoginApiView,
    UserLogoutAPIView,
    UserListAPIView,
    UserDetailAPIView,
    UserProfileUpdateAPIView
)

urlpatterns = [
    path('users/register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('users/activate/<str:uid64>/<str:token>/', activate, name='activate-account'),
    path('users/login/', UserLoginApiView.as_view(), name='user-login'),
    path('users/logout/', UserLogoutAPIView.as_view(), name='user-logout'),
    path('users/list/', UserListAPIView.as_view(), name='teacher-list'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', UserProfileUpdateAPIView.as_view(), name='update-user-profile'),
]
