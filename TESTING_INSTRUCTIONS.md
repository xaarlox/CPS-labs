# Інструкції з запуску тестів та аналізу покриття коду

## Структура тестових файлів

Тести організовані в окремій папці `users/tests/` для кращої структури проекту:

```
users/
  tests/
    __init__.py
    test_models.py      - тести для моделей (AcademicGroup, Profile)
    test_forms.py       - тести для форм (CustomUserCreationForm, ProfileForm)
    test_views.py       - тести для views (loginUser, logoutUser, registerUser, editAccount)
    test_signals.py     - тести для сигналів Django
```

## Команди для запуску тестів

### 1. Запуск всіх тестів модуля users:

```bash
python manage.py test users
```

### 2. Запуск з детальним виводом (verbosity):

```bash
python manage.py test users --verbosity=2
```

### 3. Запуск конкретного тестового файлу:

```bash
python manage.py test users.tests.test_models
python manage.py test users.tests.test_forms
python manage.py test users.tests.test_views
python manage.py test users.tests.test_signals
```

### 4. Запуск конкретного тестового класу:

```bash
python manage.py test users.tests.test_models.ProfileModelTest
python manage.py test users.tests.test_views.LoginUserViewTest
```

### 5. Запуск конкретного тесту:

```bash
python manage.py test users.tests.test_models.ProfileModelTest.test_profile_creation
```

## Аналіз покриття коду (Coverage)

### 1. Запуск тестів з вимірюванням покриття:

```bash
python -m coverage run --source=users manage.py test users
```

### 2. Перегляд звіту про покриття (консоль):

```bash
python -m coverage report
```

### 3. Генерація HTML звіту:

```bash
python -m coverage html
```

HTML звіт буде згенерований в папці `htmlcov/index.html` - відкрийте цей файл у браузері для детального перегляду.

### 4. Перегляд лише відсотка покриття:

```bash
python -m coverage report -m
```

## Результати покриття коду

На даний момент покриття коду становить **92.81%**:

- `users/models.py`: **100%** (22 рядки)
- `users/signals.py`: **100%** (24 рядки)
- `users/urls.py`: **100%** (3 рядки)
- `users/forms.py`: **97.22%** (36 рядків, пропущено 1 рядок)
- `users/views.py`: **86.59%** (82 рядки, пропущено 11 рядків)

## Типи assert, що використовуються в тестах

1. **assertEqual** - перевірка рівності значень
2. **assertNotEqual** - перевірка нерівності значень
3. **assertTrue** - перевірка що значення є True
4. **assertFalse** - перевірка що значення є False
5. **assertIsNone** - перевірка що значення є None
6. **assertIsNotNone** - перевірка що значення не є None
7. **assertIsInstance** - перевірка типу об'єкта
8. **assertIn** - перевірка наявності в колекції
9. **assertRaises** - перевірка винятку
10. **assertRedirects** - перевірка редиректу
11. **assertTemplateUsed** - перевірка використаного шаблону

## Тестові двійники (Mocks), що використовуються

1. **@patch('users.views.logout')** - мок для функції logout
2. **@patch('users.views.messages')** - мок для системи повідомлень Django
3. **@patch('users.views.login')** - мок для функції login

## Структура тестів

Тести організовані у файли та класи:

### users/tests/test_models.py

1. **AcademicGroupModelTest** - тести для моделі AcademicGroup (5 тестів)
2. **ProfileModelTest** - тести для моделі Profile (9 тестів)

### users/tests/test_forms.py

3. **CustomUserCreationFormTest** - тести для форми реєстрації (5 тестів)
4. **ProfileFormTest** - тести для форми профілю (2 тести)

### users/tests/test_views.py

5. **LoginUserViewTest** - тести для view логіну (5 тестів)
6. **LogoutUserViewTest** - тести для view виходу (3 тести)
7. **RegisterUserViewTest** - тести для view реєстрації (5 тестів)
8. **EditAccountViewTest** - тести для view редагування профілю (6 тестів)

### users/tests/test_signals.py

9. **SignalsTest** - тести для сигналів Django (3 тести)

Всього: **42 тести**, всі успішно проходять.
