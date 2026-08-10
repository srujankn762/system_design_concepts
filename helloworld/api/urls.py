from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, hello_world

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")

urlpatterns = router.urls+  [
    path("livez/", hello_world),
]