from django.db import models
from django.contrib.auth.models import User
import uuid


class AcademicGroup(models.Model):
    name = models.CharField(max_length=50)
    academic_year = models.IntegerField(default=2025)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)


    def __str__(self):
        return str(self.name)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    academic_group = models.ForeignKey(AcademicGroup, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(max_length=200, unique=True)
    bio = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to='profiles/', default="profiles/user-default.png")
    social_github = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)


    def __str__(self):
        return str(self.username)
    