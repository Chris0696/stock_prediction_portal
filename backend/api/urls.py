from django.urls import path, include
from accounts import views


urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('update-user/<int:pk>/', views.UdapteUserView.as_view()),
    path('activity-choices/', views.ActivityChoicesAPIView.as_view(), name='activity-choices'),
]