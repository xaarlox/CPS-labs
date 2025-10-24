from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Lab
from .forms import LabForm


def labs(request):
    labs = Lab.objects.all()
    context = {'labs': labs}
    return render(request, 'labs/labs.html', context)


def lab(request, pk):
    labObj = Lab.objects.get(id=pk)
    return render(request, 'labs/single-lab.html', {'lab': labObj})


def createLab(request):
    form = LabForm()
    if request.method == 'POST':
        form = LabForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('labs')
    context = {'form': form}
    return render(request, "labs/lab_form.html", context)


def updateLab(request, pk):
    lab = Lab.objects.get(id=pk)
    form = LabForm(instance=lab)
    if request.method == 'POST':
        form = LabForm(request.POST, instance=lab)
        if form.is_valid():
            form.save()
            return redirect('labs')
    context = {'form': form}
    return render(request, "labs/lab_form.html", context)


def deleteLab(request, pk):
    lab = Lab.objects.get(id=pk)
    if request.method == 'POST':
        lab.delete()
        return redirect('labs')
    context = {'object': lab}
    return render(request, 'labs/delete_template.html', context)