from django.urls import path
from . import views

urlpatterns = [
    path('', views.labs, name="labs"),
    path('lab/<str:pk>/', views.lab, name="lab"),
    path('create-lab/', views.createLab, name="create-lab"),
    path('update-lab/<str:pk>/', views.updateLab, name="update-lab"),
    path('delete-lab/<str:pk>/', views.deleteLab, name="delete-lab"),
]