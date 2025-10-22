from django.shortcuts import render
from django.http import HttpResponse


labList = [
    {
        'id': '1',
        'title': 'Ecommerce Website',
        'description': 'Fully functional ecommerce website'
    },
    {
        'id': '2',
        'title': 'Portfolio Website',
        'description': 'A personal website to write articles and display work'
    },
    {
        'id': '3',
        'title': 'Social Network',
        'description': 'An open source project built by the community'
    }
]


def labs(request):
    page = "labs"
    number = 10
    context = {'page': page, 'number': number, 'labs': labList}
    return render(request, 'labs/labs.html', context)


def lab(request, pk):
    labObj = None
    for i in labList:
        if i['id'] == pk:
            labObj = i
    return render(request, 'labs/single-lab.html', {'lab': labObj})
