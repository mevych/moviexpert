from django.shortcuts import render

from .models import Movie

def home(request):
    return render(request, "main/home.html", {"movies_total": Movie.objects.count()})