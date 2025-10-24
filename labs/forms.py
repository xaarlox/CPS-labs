from django.forms import ModelForm
from .models import Lab


class LabForm(ModelForm):
    class Meta:
        model = Lab
        fields = ['title', 'description', 'order', 'passing_mark', 'max_mark', 'max_attempts', 'deadline', 'is_active']