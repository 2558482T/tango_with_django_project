from django.shortcuts import render
from django.http import HttpResponse

# each function is a view
def index(request):
    return HttpResponse("Rango says hey there partner!")
