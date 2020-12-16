from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import datetime


def index(request):
    """
    ROC landing page.
    """
    index_context = {}
    return render(request, 'website/index.html', index_context)
