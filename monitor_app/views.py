from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def initial(request):
    return HttpResponse("Hello, World!")

