from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('labs/', views.labs, name="labs"),
    path('lab/<str:pk>/', views.lab, name="lab"),
    path('lab/<str:pk>/cps-simulation/', views.cps_simulation, name="cps_simulation"),
    path('api/simulate-step/', views.simulate_step, name="simulate_step"),
    path('api/calculate-score/', views.calculate_score, name="calculate_score"),
    path('api/submit-ballistics/', views.submit_ballistics_result, name="submit_ballistics"),
    path('api/submit-cps/', views.submit_cps_result, name="submit_cps"),
]