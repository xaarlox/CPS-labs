from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        labels = {
            'first_name': 'Ім\'я',
            'last_name': 'Прізвище',
            'username': 'Логін',
            'email': 'Електронна пошта',
            'password1': 'Пароль',
            'password2': 'Підтвердження пароля',
        }

    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # If email is empty
        if not email:
            raise ValidationError("Будь ласка, введіть email-адресу.")
            
        # Validate email format
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            raise ValidationError("Некоректний формат email-адреси.")
            
        # Check for unique email
        if User.objects.filter(email=email).exists():
            raise ValidationError("Користувач із такою email-адресою вже існує.")
            
        return email
        