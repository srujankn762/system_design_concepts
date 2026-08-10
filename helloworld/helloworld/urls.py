from django.contrib import admin
from django.urls import path, include
from helloworld.api.views import hello_world

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))
]