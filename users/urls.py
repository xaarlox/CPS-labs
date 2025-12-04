from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),
    path('edit-account/', views.editAccount, name='edit-account'),
    path('users/<uuid:pk>/edit/', views.admin_edit_user, name='admin-edit-user'),
    path('users/<uuid:pk>/delete/', views.admin_delete_user, name='admin-delete-user'),
]