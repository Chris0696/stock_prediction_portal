from django.urls import path, include
from accounts import views as UserViews
from rest_framework_simplejwt.views import TokenRefreshView
from .views import StockPredictionAPIView


urlpatterns = [
    path('register/', UserViews.RegisterView.as_view()),
    path('update-user/<int:pk>/', UserViews.UdapteUserView.as_view()),

    path('login/', UserViews.LoginAPIView.as_view(), name='login'),
    path('token/', UserViews.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('activity-choices/', UserViews.ActivityChoicesAPIView.as_view(), name='activity-choices'),
    

    path('protected-view/', UserViews.ProtectedView.as_view()),

    # Rates data
    # path('rates/', RatesAPIView.as_view(), name='rates-api'),

    # Prediction API
    path('predict/', StockPredictionAPIView.as_view(), name='stock_prediction'),
]