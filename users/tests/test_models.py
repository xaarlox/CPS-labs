from django.test import TestCase
from django.contrib.auth.models import User
import uuid

from users.models import AcademicGroup, Profile


class AcademicGroupModelTest(TestCase):
    
    def setUp(self):
        self.group = AcademicGroup.objects.create(
            name='Група 1',
            academic_year=2025
        )
    
    def test_academic_group_creation(self):
        self.assertIsNotNone(self.group.id)
        self.assertEqual(self.group.name, 'Група 1')
        self.assertEqual(self.group.academic_year, 2025)
    
    def test_academic_group_str_representation(self):
        self.assertEqual(str(self.group), 'Група 1')
    
    def test_academic_group_uuid_generation(self):
        self.assertIsInstance(self.group.id, uuid.UUID)
        self.assertIsNotNone(self.group.id)
    
    def test_academic_group_default_year(self):
        group2 = AcademicGroup.objects.create(name='Група 2')
        self.assertEqual(group2.academic_year, 2025)
    
    def test_academic_group_uniqueness(self):
        group2 = AcademicGroup.objects.create(name='Група 3')
        self.assertNotEqual(self.group.id, group2.id)


class ProfileModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.academic_group = AcademicGroup.objects.create(name='Група 1')
        # Профіль створюється автоматично через сигнал
        self.profile = Profile.objects.get(user=self.user)
        # Оновлення профілю для тестів
        self.profile.name = 'Test User'
        self.profile.academic_group = self.academic_group
        self.profile.bio = 'Test bio'
        self.profile.save()
    
    def test_profile_creation(self):
        self.assertIsNotNone(self.profile.id)
        self.assertEqual(self.profile.name, 'Test User')
        self.assertEqual(self.profile.username, 'testuser')
        self.assertEqual(self.profile.email, 'test@example.com')
    
    def test_profile_str_representation(self):
        self.assertEqual(str(self.profile), 'testuser')
    
    def test_profile_user_relationship(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertTrue(self.profile.user.is_authenticated)
    
    def test_profile_academic_group_relationship(self):
        self.assertEqual(self.profile.academic_group, self.academic_group)
        self.assertIsNotNone(self.profile.academic_group)
    
    def test_profile_default_image(self):
        self.assertTrue(self.profile.profile_image)
        self.assertIn('user-default.png', str(self.profile.profile_image))
    
    def test_profile_uuid_generation(self):
        self.assertIsInstance(self.profile.id, uuid.UUID)
    
    def test_profile_email_uniqueness(self):
        user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@example.com'
        )
        with self.assertRaises(Exception):
            profile2 = Profile.objects.get(user=user2)
            profile2.email = 'test@example.com'  # Дублікат
            profile2.save()
    
    def test_profile_optional_fields(self):
        user2 = User.objects.create_user(
            username='user2', 
            email='user2@example.com',
            first_name='',
            last_name=''
        )
        # Профіль створюється автоматично через сигнал
        profile2 = Profile.objects.get(user=user2)
        # Перевірка, що опціональні поля можуть бути порожніми або None
        self.assertTrue(profile2.name is None or profile2.name == '')
        self.assertIsNone(profile2.bio)
        self.assertIsNone(profile2.social_github)

