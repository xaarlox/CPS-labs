from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from io import BytesIO
from PIL import Image

from users.models import Profile


class LoginUserViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.login_url = reverse('login')
    
    def test_login_view_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login_register.html')
    
    def test_login_view_successful_login(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_authenticated_user_redirect(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('home'))


class LogoutUserViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.logout_url = reverse('logout')
    
    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        self.assertTrue(self.client.login(username='testuser', password='testpass123'))
        
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    @patch('users.views.logout')
    def test_logout_view_calls_logout_function(self, mock_logout):
        """Тест виклику функції logout з використанням мока"""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.logout_url)
        self.assertTrue(mock_logout.called)
    
    @patch('users.views.messages')
    def test_logout_view_shows_message(self, mock_messages):
        """Тест відображення повідомлення при виході"""
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.logout_url)
        mock_messages.info.assert_called_once()


class RegisterUserViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_register_view_get_request(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login_register.html')
        self.assertIn('form', response.context)
    
    def test_register_view_successful_registration(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, form_data)
        self.assertRedirects(response, reverse('edit-account'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_register_view_invalid_data(self):
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    @patch('users.views.messages')
    def test_register_view_success_message(self, mock_messages):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        self.client.post(self.register_url, form_data)
        mock_messages.success.assert_called_once()
    
    @patch('users.views.login')
    def test_register_view_calls_login(self, mock_login):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        self.client.post(self.register_url, form_data)
        self.assertTrue(mock_login.called)


class EditAccountViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        # Профіль створюється автоматично через сигнал
        self.profile = Profile.objects.get(user=self.user)
        self.profile.name = 'Test User'
        self.profile.save()
        self.edit_url = reverse('edit-account')
    
    def test_edit_account_view_requires_login(self):
        response = self.client.get(self.edit_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.edit_url}")
    
    def test_edit_account_view_get_request(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_form.html')
        self.assertIn('form', response.context)
        self.assertIn('profile', response.context)
        self.assertIn('password_form', response.context)
    
    def test_edit_account_view_update_profile(self):
        self.client.login(username='testuser', password='testpass123')
        form_data = {
            'update_profile': '1',
            'name': 'Updated Name',
            'username': 'updateduser',
            'email': 'updated@example.com',
            'bio': 'Updated bio'
        }
        response = self.client.post(self.edit_url, form_data)
        self.assertRedirects(response, self.edit_url)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'Updated Name')
        self.assertEqual(self.profile.username, 'updateduser')
    
    def test_edit_account_view_change_password(self):
        self.client.login(username='testuser', password='testpass123')
        form_data = {
            'change_password': '1',
            'old_password': 'testpass123',
            'new_password1': 'NewPass123!',
            'new_password2': 'NewPass123!'
        }
        response = self.client.post(self.edit_url, form_data)
        self.assertRedirects(response, self.edit_url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))
    
    def test_edit_account_view_update_avatar(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Створюємо тестове зображення
        image = Image.new('RGB', (100, 100), color='blue')
        image_file = BytesIO()
        image.save(image_file, 'PNG')
        image_file.seek(0)
        
        uploaded_image = SimpleUploadedFile(
            'avatar.png',
            image_file.read(),
            content_type='image/png'
        )
        
        form_data = {
            'update_avatar': '1'
        }
        response = self.client.post(self.edit_url, form_data, files={'profile_image': uploaded_image})
        self.assertRedirects(response, self.edit_url)
    
    @patch('users.views.messages')
    def test_edit_account_view_success_message(self, mock_messages):
        self.client.login(username='testuser', password='testpass123')
        form_data = {
            'update_profile': '1',
            'name': 'Updated Name',
            'username': 'testuser',
            'email': 'test@example.com'
        }
        self.client.post(self.edit_url, form_data)
        mock_messages.success.assert_called_once()



