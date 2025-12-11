from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.db import connection, IntegrityError, transaction

from labs.models import Lab, Submission, Attempt, CyberPhysicalSystemSimulation


class LabDatabaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='pass123',
            first_name='Student',
            last_name='One',
        )
        self.lab = Lab.objects.create(
            title='Control System Lab',
            order=1,
            max_attempts=3,
            passing_mark=60,
            max_mark=100,
            is_active=True,
        )
        self.submission = Submission.objects.create(
            lab=self.lab,
            profile=self.user.profile,
            attempts_left=self.lab.max_attempts,
        )

    def _create_attempt_with_simulation(self, mark: float = 75.0, attempt_number: int = 1):
        attempt = Attempt.objects.create(
            submission=self.submission,
            mark=mark,
            attempt_number=attempt_number,
            answers={'note': f'attempt {attempt_number}'},
        )
        simulation = CyberPhysicalSystemSimulation.objects.create(
            attempt=attempt,
            lab_type='water_tank',
            state='running',
            initial_value=0,
            target_value=100,
            current_value=20,
            error_threshold=0.5,
            kp=0.6,
            ki=0.1,
            kd=0.2,
            simulation_time=1.5,
            total_duration=120,
            simulation_data=[{'time': 0, 'value': 20, 'error': 80}],
            success=False,
            final_score=0,
        )
        return attempt, simulation

    def test_master_detail_chain_creation(self):
        attempt, simulation = self._create_attempt_with_simulation()

        self.assertEqual(self.lab.submissions.count(), 1)
        self.assertEqual(self.submission.lab, self.lab)
        self.assertEqual(self.submission.profile.user.username, 'student1')
        self.assertEqual(self.submission.attempts.count(), 1)
        self.assertEqual(attempt.submission, self.submission)
        self.assertEqual(simulation.attempt, attempt)
        self.assertEqual(attempt.cps_simulation, simulation)

    def test_attempt_numbering_and_best_mark_tracking(self):
        first_attempt, _ = self._create_attempt_with_simulation(mark=65.0, attempt_number=1)
        second_attempt, _ = self._create_attempt_with_simulation(mark=92.0, attempt_number=2)

        attempts = list(self.submission.attempts.all())
        self.assertEqual([a.attempt_number for a in attempts], [1, 2])

        # Емулюємо бізнес-логіку оновлення submission після нової спроби
        self.submission.attempts_left -= 2
        self.submission.best_mark = max(a.mark for a in attempts)
        self.submission.status = 'submitted'
        self.submission.save()

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.best_mark, 92.0)
        self.assertEqual(self.submission.attempts_left, self.lab.max_attempts - 2)
        self.assertEqual(self.submission.status, 'submitted')
        self.assertEqual(self.submission.attempts.order_by('-mark').first(), second_attempt)

    def test_cascade_delete_on_submission_removes_attempts_and_simulations(self):
        attempt, simulation = self._create_attempt_with_simulation()

        self.submission.delete()

        self.assertFalse(Attempt.objects.filter(id=attempt.id).exists())
        self.assertFalse(CyberPhysicalSystemSimulation.objects.filter(id=simulation.id).exists())
        self.assertEqual(Lab.objects.count(), 1)


class DatabaseComponentTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(
            username='dbstudent',
            email='dbstudent@example.com',
            password='pass123',
            first_name='DB',
            last_name='Student',
        )
        self.lab = Lab.objects.create(
            title='DB Lab',
            order=2,
            max_attempts=2,
            passing_mark=50,
            max_mark=100,
            is_active=True,
        )
        self.submission = Submission.objects.create(
            lab=self.lab,
            profile=self.user.profile,
            attempts_left=self.lab.max_attempts,
        )

    def _get_columns(self, table_name):
        with connection.cursor() as cursor:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            return {row[1] for row in cursor.fetchall()}

    def test_lab_table_columns_present(self):
        columns = self._get_columns('labs_lab')
        expected = {
            'id',
            'title',
            'description',
            'order',
            'passing_mark',
            'max_mark',
            'max_attempts',
            'created_at',
            'deadline',
            'is_active',
        }
        self.assertTrue(expected.issubset(columns))

    def test_attempt_table_columns_present(self):
        columns = self._get_columns('labs_attempt')
        expected = {'id', 'submission_id', 'mark', 'created_at', 'attempt_number', 'answers'}
        self.assertTrue(expected.issubset(columns))

    def test_foreign_keys_and_on_delete_behaviour(self):
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_key_list('labs_submission')")
            fk_rows = cursor.fetchall()
        # Map source column -> (target_table, on_delete)
        fk_map = {row[3]: (row[2], row[6]) for row in fk_rows}
        # SQLite іноді відображає CASCADE як NO ACTION у схемі; дозволяємо обидва
        self.assertIn(fk_map.get('lab_id'), [('labs_lab', 'CASCADE'), ('labs_lab', 'NO ACTION')])
        self.assertIn(fk_map.get('profile_id'), [('users_profile', 'CASCADE'), ('users_profile', 'NO ACTION')])

        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_key_list('labs_attempt')")
            attempt_fk_rows = cursor.fetchall()
        attempt_fk_map = {row[3]: (row[2], row[6]) for row in attempt_fk_rows}
        self.assertIn(attempt_fk_map.get('submission_id'), [('labs_submission', 'CASCADE'), ('labs_submission', 'NO ACTION')])

    def test_cascade_delete_via_sql(self):
        # Створюємо спробу, щоб перевірити фактичне каскадне видалення
        attempt = Attempt.objects.create(
            submission=self.submission,
            mark=70,
            attempt_number=1,
            answers={'note': 'raw-cascade'},
        )
        # Видаляємо Lab через ORM, що під капотом викликає каскад на БД/ORM
        self.lab.delete()

        # Перевіряємо, що дочірні записи зникли
        self.assertFalse(Submission.objects.filter(id=self.submission.id).exists())
        self.assertFalse(Attempt.objects.filter(id=attempt.id).exists())

    def test_one_to_one_simulation_uniqueness_enforced(self):
        attempt = Attempt.objects.create(
            submission=self.submission,
            mark=80,
            attempt_number=1,
            answers={'note': 'unique-check'},
        )
        CyberPhysicalSystemSimulation.objects.create(
            attempt=attempt,
            lab_type='water_tank',
            state='running',
            initial_value=0,
            target_value=100,
            current_value=10,
            error_threshold=0.5,
            kp=0.5,
            ki=0.1,
            kd=0.2,
            simulation_time=0.5,
            total_duration=120,
            simulation_data=[{'time': 0, 'value': 10, 'error': 90}],
            success=False,
            final_score=0,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CyberPhysicalSystemSimulation.objects.create(
                    attempt=attempt,
                    lab_type='water_tank',
                    state='running',
                    initial_value=0,
                    target_value=100,
                    current_value=15,
                    error_threshold=0.5,
                    kp=0.5,
                    ki=0.1,
                    kd=0.2,
                    simulation_time=1.0,
                    total_duration=120,
                    simulation_data=[{'time': 1, 'value': 15, 'error': 85}],
                    success=False,
                    final_score=0,
                )
