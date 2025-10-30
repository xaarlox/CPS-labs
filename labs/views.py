from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Lab


def home(request):
    return render(request, 'home.html')


@login_required(login_url='login')
def labs(request):
    labs = Lab.objects.all()
    context = {'labs': labs}
    return render(request, 'labs/labs.html', context)


@login_required(login_url='login')
def lab(request, pk):
    labObj = Lab.objects.get(id=pk)
    return render(request, 'labs/lab.html', {'lab': labObj})
