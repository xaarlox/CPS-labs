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


class CyberPhysicalSystemSimulation(models.Model):
    """
    Модель для зберігання даних симуляції кіберфізичної системи
    """
    LAB_TYPE_CHOICES = [
        ('water_tank', 'Система контролю рівня води'),
        ('temperature', 'Система контролю температури'),
        ('speed_control', 'Система контролю швидкості'),
        ('pressure', 'Система контролю тиску'),
    ]
    
    STATE_CHOICES = [
        ('running', 'Запущена'),
        ('paused', 'Призупинена'),
        ('stopped', 'Зупинена'),
    ]
    
    attempt = models.OneToOneField(Attempt, on_delete=models.CASCADE, related_name='cps_simulation')
    lab_type = models.CharField(max_length=50, choices=LAB_TYPE_CHOICES, default='water_tank')
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='stopped')
    
    # Параметри системи
    initial_value = models.FloatField(help_text="Початкове значення")
    target_value = models.FloatField(help_text="Значення, до якого потрібно дійти")
    current_value = models.FloatField(help_text="Поточне значення системи")
    error_threshold = models.FloatField(default=0.5, help_text="Допустимої відхилення")
    
    # Контролер (PID параметри)
    kp = models.FloatField(default=0.5, help_text="Коефіцієнт P")
    ki = models.FloatField(default=0.1, help_text="Коефіцієнт I")
    kd = models.FloatField(default=0.2, help_text="Коефіцієнт D")
    
    # Часові параметри
    simulation_time = models.FloatField(default=0, help_text="Поточний час симуляції (сек)")
    total_duration = models.FloatField(default=120, help_text="Загальна тривалість (сек)")
    
    # Результати
    simulation_data = models.JSONField(default=list, help_text="Масив точок даних: [{'time': ..., 'value': ..., 'error': ...}]")
    success = models.BooleanField(default=False, help_text="Чи досягнута мета")
    final_score = models.FloatField(default=0, help_text="Підсумковий бал (0-100)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"CPS Simulation ({self.lab_type}) - {self.attempt}"