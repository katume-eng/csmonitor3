from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from .models import Location, Collected, CongestionLevel

def initial(request):
    return HttpResponse("Hello, World!")