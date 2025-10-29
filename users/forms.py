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
        }


    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Підтвердження пароля'

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input', 'required': 'required', 'placeholder': ' '})

    
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
        