from django.db import models
import uuid


class Lab(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    max_mark = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.title