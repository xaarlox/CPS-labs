from django.urls import path
from . import views

urlpatterns = [
    path('', views.labs, name="labs"),
    path('lab/<str:pk>/', views.lab, name="lab"),
]