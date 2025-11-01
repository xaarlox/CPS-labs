from django.test import TestCase
from django.contrib.auth.models import User

from users.models import Profile


class SignalsTest(TestCase):
    
    def test_create_profile_signal(self):
        user = User.objects.create_user(
            username='newsignaluser',
            email='signal@example.com',
            password='testpass123',
            first_name='Signal',
            last_name='User'
        )
        # Перевірка, що профіль був створений через сигнал
        self.assertTrue(Profile.objects.filter(user=user).exists())
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.email, user.email)
        self.assertEqual(profile.username, user.username)
        self.assertEqual(profile.name, 'Signal User')
    
    def test_update_user_signal(self):
        user = User.objects.create_user(
            username='updatesignaluser',
            email='updatesignal@example.com',
            password='testpass123'
        )
        profile = Profile.objects.get(user=user)
        
        profile.name = 'Updated Signal Name'
        profile.username = 'updatedsignaluser'
        profile.email = 'updatedsignal@example.com'
        profile.save()
        
        user.refresh_from_db()
        self.assertEqual(user.email, 'updatedsignal@example.com')
        self.assertEqual(user.username, 'updatedsignaluser')
    
    def test_delete_user_signal(self):
        user = User.objects.create_user(
            username='deletesignaluser',
            email='deletesignal@example.com',
            password='testpass123'
        )
        profile = Profile.objects.get(user=user)
        user_id = user.id
        
        profile.delete()
        
        # Перевірка що користувач також був видалений
        self.assertFalse(User.objects.filter(id=user_id).exists())

