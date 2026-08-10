from rest_framework.viewsets import ModelViewSet
from .models import Employee
from .serializers import EmployeeSerializer
from django.http import JsonResponse


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


def hello_world(request):
    return JsonResponse({
        "message": "Hello World!",
        "status": "success"
    })