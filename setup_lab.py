
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpslabs.settings')
django.setup()

from labs.models import Lab
from django.utils import timezone
from datetime import timedelta
from django.db.utils import OperationalError as DBError
from django.core.management import call_command

try:
    try:
        call_command('makemigrations', interactive=False)
        call_command('migrate', interactive=False)
        print("Міграції виконані успішно.")
    except Exception as me:
        print("Не вдалося автоматично виконати міграції: ", me)
        print("Спробуйте самостійно:")
        print("  python manage.py makemigrations")
        print("  python manage.py migrate")
        raise

    Lab.objects.all().delete()
    print("Всі старі лаби видалені")

    lab = Lab.objects.create(
        title="Балістика",
        description="Лабораторна робота: Балістична траєкторія. Розрахуйте оптимальні параметри пострілу для влучення снаряда в ціль з урахуванням опору повітря. Маса снаряда — 2 кг, радіус — 0.15 м. Ціль розташована на 15 м з висотою 2 м. Визначте кут та початкову швидкість.",
        order=1,
        passing_mark=60,
        max_mark=100,
        max_attempts=10,
        deadline=timezone.now() + timedelta(days=30),
        is_active=True,
    )
    print(f"Лаба додана: {lab.title} (ID: {lab.id})")

    thermo = Lab.objects.create(
        title="Термодинаміка",
        description=(
            "Лабораторна робота: Ідеальний газ у циліндрі з поршнем. "
            "Керуйте об'ємом і температурою, виміряйте тиск і обчисліть кількість речовини n за законом ідеального газу (pV = nRT). "
            "Інтерактивна симуляція містить поршень, індикатори тиску/об'єму/температури і поле для введення n."
        ),
        order=2,
        passing_mark=50,
        max_mark=100,
        max_attempts=5,
        deadline=timezone.now() + timedelta(days=30),
        is_active=True,
    )
    print(f"Лаба додана: {thermo.title} (ID: {thermo.id})")

    print("\nВсі лаби:")
    for lab in Lab.objects.all().order_by('order'):
        print(f"  {lab.order}. {lab.title}")
except DBError as e:
    print("Помилка доступу до бази даних:", e)
    print("Схоже, що таблиць все ще немає або сталася інша помилка при роботі з БД.")
    print("Виконайте в терміналі:")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate")
    print("Після успішних міграцій запустіть цей скрипт знову:")
    print("  python setup_lab.py")