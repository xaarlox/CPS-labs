from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

from users.models import AcademicGroup, Profile
from users.forms import CustomUserCreationForm, ProfileForm


class CustomUserCreationFormTest(TestCase):
    
    def test_form_valid_data(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_email_format(self):
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_duplicate_email(self):
        User.objects.create_user(username='existing', email='existing@example.com')
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_empty_email(self):
        form_data = {
            'username': 'newuser',
            'email': '',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_password_mismatch(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass456!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class ProfileFormTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.academic_group = AcademicGroup.objects.create(name='Група 1')
        # Профіль створюється автоматично через сигнал
        self.profile = Profile.objects.get(user=self.user)
    
    def test_form_valid_data(self):
        form_data = {
            'name': 'Updated Name',
            'username': 'updateduser',
            'email': 'updated@example.com',
            'bio': 'Updated bio',
            'academic_group': self.academic_group.id,
            'social_github': 'github.com/user'
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
    
    def test_form_with_image(self):
        # Створення тестового зображення
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        
        uploaded_image = SimpleUploadedFile(
            'test_image.png',
            image_file.read(),
            content_type='image/png'
        )
        
        form_data = {
            'name': 'Test User',
            'username': 'testuser',
            'email': 'test@example.com'
        }
        form = ProfileForm(data=form_data, files={'profile_image': uploaded_image}, instance=self.profile)
        self.assertTrue(form.is_valid())



