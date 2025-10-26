from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def hello(request):
    return HttpResponse("<h1>Hello FreeCups! ☕🎉</h1><p>FreeCups project is running successfully!</p>")
