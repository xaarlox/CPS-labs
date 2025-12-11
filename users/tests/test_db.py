from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.db import connection, IntegrityError, transaction

from users.models import AcademicGroup, Profile


class UsersDatabaseComponentTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.group = AcademicGroup.objects.create(name='DB Group', academic_year=2025)
        self.user = User.objects.create_user(
            username='dbuser',
            email='dbuser@example.com',
            password='pass123',
            first_name='DB',
            last_name='User',
        )
        self.profile = Profile.objects.get(user=self.user)
        self.profile.academic_group = self.group
        self.profile.save()

    def _columns(self, table):
        with connection.cursor() as cursor:
            cursor.execute(f"PRAGMA table_info('{table}')")
            return {row[1] for row in cursor.fetchall()}

    def test_profile_table_columns(self):
        columns = self._columns('users_profile')
        expected = {
            'id',
            'user_id',
            'name',
            'username',
            'academic_group_id',
            'email',
            'bio',
            'profile_image',
            'social_github',
            'created_at',
            'is_admin',
        }
        self.assertTrue(expected.issubset(columns))

    def test_academic_group_table_columns(self):
        columns = self._columns('users_academicgroup')
        expected = {'id', 'name', 'academic_year'}
        self.assertTrue(expected.issubset(columns))

    def test_foreign_keys(self):
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_key_list('users_profile')")
            fk_rows = cursor.fetchall()
        fk_map = {row[3]: (row[2], row[6]) for row in fk_rows}

        # SQLite може відображати CASCADE як NO ACTION у схемі
        self.assertIn(fk_map.get('user_id'), [('auth_user', 'CASCADE'), ('auth_user', 'NO ACTION')])
        self.assertIn(fk_map.get('academic_group_id'), [('users_academicgroup', 'SET NULL'), ('users_academicgroup', 'NO ACTION')])

    def test_delete_user_cascades_profile(self):
        self.user.delete()
        self.assertFalse(Profile.objects.filter(id=self.profile.id).exists())

    def test_delete_group_sets_null(self):
        self.group.delete()
        self.profile.refresh_from_db()
        self.assertIsNone(self.profile.academic_group)

    def test_email_uniqueness_enforced(self):
        user2 = User.objects.create_user(
            username='dbuser2',
            email='dbuser2@example.com',
            password='pass123',
        )
        profile2 = Profile.objects.get(user=user2)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                profile2.email = self.profile.email
                profile2.save()
