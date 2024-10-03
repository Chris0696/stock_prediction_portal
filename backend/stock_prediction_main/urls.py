from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Base API EndPoint

    path('api/v1/', include('api.urls'))
]
