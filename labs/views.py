from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Lab


def home(request):
    return render(request, 'home.html')


def labs(request):
    labs = Lab.objects.all()
    context = {'labs': labs}
    return render(request, 'labs/labs.html', context)


def lab(request, pk):
    labObj = Lab.objects.get(id=pk)
    return render(request, 'labs/lab.html', {'lab': labObj})
