from django.db import models
import uuid
from users.models import Profile


class Lab(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0)
    passing_mark = models.FloatField(null=True, blank=True)
    max_mark = models.FloatField(null=True, blank=True)
    max_attempts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)


    class Meta:
        ordering = ['order']


    def __str__(self):
        return self.title
    

class Submission(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='submissions')
    profile = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='not submitted')
    best_mark = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attempts_left = models.IntegerField()
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)


    def __str__(self):
        return f"Submission for {self.lab.title} by {self.profile.user.username}"


class Attempt(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='attempts')
    mark = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attempt_number = models.IntegerField()
    answers = models.JSONField(null=True, blank=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)


    class Meta:
        ordering = ['created_at']

    
    def __str__(self):
        return f"Attempt #{self.attempt_number} for submission ID {self.submission.id}"