from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, ProfileForm, AdminProfileUpdateForm
from .models import Profile, AcademicGroup
from labs.models import Lab, Submission


def loginUser(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'users/login_register.html')


def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('home')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created!')

            login(request, user)
            return redirect('edit-account')
        
        else:
            messages.error(request, 'An error occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)


@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    user = request.user

    # Дані для вкладки "Перегляд учасників" (тільки для адміна)
    grouped_students = []
    admins = []
    unknown_users = []
    performance_groups = []
    labs_for_performance = []
    if profile.is_admin:
        groups = AcademicGroup.objects.all().order_by('name')

        # Перші три лабораторні для розділу "Успішність студентів"
        labs_for_performance = list(Lab.objects.order_by('order')[:3])

        for group in groups:
            students_in_group = Profile.objects.filter(
                is_admin=False,
                academic_group=group,
            ).order_by('name')
            if students_in_group.exists():
                grouped_students.append((group, students_in_group))

                # Формуємо дані для успішності по кожній групі
                group_rows = []
                for student in students_in_group:
                    # за замовчуванням 0 для оцінок і max_attempts для спроб
                    mark1 = mark2 = mark3 = 0
                    attempts1 = attempts2 = attempts3 = 0

                    if len(labs_for_performance) > 0:
                        lab1 = labs_for_performance[0]
                        attempts1 = lab1.max_attempts  # за замовчуванням максимальна кількість спроб
                        sub1 = Submission.objects.filter(
                            lab=lab1,
                            profile=student,
                        ).order_by('-created_at').first()
                        if sub1:
                            if sub1.best_mark is not None:
                                mark1 = sub1.best_mark
                            attempts1 = sub1.attempts_left

                    if len(labs_for_performance) > 1:
                        lab2 = labs_for_performance[1]
                        attempts2 = lab2.max_attempts
                        sub2 = Submission.objects.filter(
                            lab=lab2,
                            profile=student,
                        ).order_by('-created_at').first()
                        if sub2:
                            if sub2.best_mark is not None:
                                mark2 = sub2.best_mark
                            attempts2 = sub2.attempts_left

                    if len(labs_for_performance) > 2:
                        lab3 = labs_for_performance[2]
                        attempts3 = lab3.max_attempts
                        sub3 = Submission.objects.filter(
                            lab=lab3,
                            profile=student,
                        ).order_by('-created_at').first()
                        if sub3:
                            if sub3.best_mark is not None:
                                mark3 = sub3.best_mark
                            attempts3 = sub3.attempts_left

                    group_rows.append({
                        'student': student,
                        'mark1': mark1,
                        'mark2': mark2,
                        'mark3': mark3,
                        'attempts1': attempts1,
                        'attempts2': attempts2,
                        'attempts3': attempts3,
                    })

                performance_groups.append((group, group_rows))

        # Викладачі (адміністратори), крім поточного користувача
        admins = Profile.objects.filter(
            is_admin=True,
        ).exclude(pk=profile.pk).order_by('name')

        # "Невідомі" користувачі: без групи і не адміністратори
        unknown_users = Profile.objects.filter(
            is_admin=False,
            academic_group__isnull=True,
        ).order_by('name')

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успішно змінено!')
                return redirect(reverse('edit-account') + '?section=account')
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                form = ProfileForm(instance=profile)
                password_form = PasswordChangeForm(user)
                # Не робимо редирект при помилках - рендеримо сторінку знову
                # active_section буде використано в шаблоні для відкриття правильної вкладки
        elif 'update_avatar' in request.POST:
            if 'profile_image' in request.FILES:
                profile.profile_image = request.FILES['profile_image']
                profile.save()
                messages.success(request, 'Аватар успішно оновлено!')
            return redirect(reverse('edit-account') + '?section=profile')

        elif 'update_profile' in request.POST:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                user.first_name = request.POST.get('first_name', user.first_name)
                user.last_name = request.POST.get('last_name', user.last_name)
                user.save()
                messages.success(request, 'Профіль успішно оновлено!')
                return redirect(reverse('edit-account') + '?section=profile')
            else:
                messages.error(request, 'Сталася помилка під час збереження профілю.')
                password_form = PasswordChangeForm(user)
                # Не робимо редирект при помилках - рендеримо сторінку знову
        else:
            form = ProfileForm(instance=profile)
            password_form = PasswordChangeForm(user)
    else:
        form = ProfileForm(instance=profile)
        password_form = PasswordChangeForm(user)

    # Визначаємо активну вкладку на основі POST параметрів або URL параметра
    active_section = request.GET.get('section', 'profile')
    if request.method == 'POST':
        if 'change_password' in request.POST:
            active_section = 'account'
        elif 'update_profile' in request.POST or 'update_avatar' in request.POST:
            active_section = 'profile'

    context = {
        'form': form,
        'profile': profile,
        'password_form': password_form,
        'grouped_students': grouped_students,
        'admins': admins,
        'unknown_users': unknown_users,
        'performance_groups': performance_groups,
        'labs_for_performance': labs_for_performance,
        'active_section': active_section,
    }
    return render(request, 'users/profile_form.html', context)


@login_required(login_url='login')
def admin_edit_user(request, pk):
    if not request.user.profile.is_admin:
        return redirect('edit-account')

    profile_obj = get_object_or_404(Profile, pk=pk)

    if request.method == 'POST':
        form = AdminProfileUpdateForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дані користувача успішно оновлено.')
            return redirect(reverse('edit-account') + '?section=teacher')
    else:
        form = AdminProfileUpdateForm(instance=profile_obj)

    context = {'form': form, 'edited_profile': profile_obj}
    return render(request, 'users/admin_edit_user.html', context)


@login_required(login_url='login')
def admin_delete_user(request, pk):
    if not request.user.profile.is_admin:
        return redirect('edit-account')

    profile_obj = get_object_or_404(Profile, pk=pk)

    if request.method == 'POST':
        full_name = profile_obj.name or profile_obj.username
        profile_obj.delete()
        messages.success(request, f'Користувача "{full_name}" видалено.')
        return redirect(reverse('edit-account') + '?section=teacher')

    context = {'profile_to_delete': profile_obj}
    return render(request, 'users/admin_confirm_delete.html', context)


@login_required(login_url='login')
def admin_edit_attempts(request, pk):
    """Редагування кількості спроб по перших трьох лабораторних для одного студента."""
    if not request.user.profile.is_admin:
        return redirect('edit-account')

    student_profile = get_object_or_404(Profile, pk=pk, is_admin=False)
    labs_for_performance = list(Lab.objects.order_by('order')[:3])

    # Отримати поточні значення
    current_data = []
    for lab in labs_for_performance:
        submission = Submission.objects.filter(lab=lab, profile=student_profile).order_by('-created_at').first()
        # Якщо Submission немає, використовуємо max_attempts з лабораторної
        attempts = submission.attempts_left if submission else lab.max_attempts
        current_data.append({'lab': lab, 'attempts': attempts})

    if request.method == 'POST':
        for idx, lab in enumerate(labs_for_performance):
            field_name = f'attempts_{idx + 1}'
            value = request.POST.get(field_name, '').strip()
            if value == '':
                continue
            try:
                attempts_val = int(value)
                if attempts_val < 0:
                    attempts_val = 0
            except ValueError:
                continue

            submission, created = Submission.objects.get_or_create(
                lab=lab,
                profile=student_profile,
                defaults={
                    'status': 'not submitted',
                    'best_mark': 0,
                    'attempts_left': attempts_val,
                },
            )
            if not created:
                submission.attempts_left = attempts_val
                submission.save()

        messages.success(request, 'Кількість спроб для студента оновлено.')
        return redirect(reverse('edit-account') + '?section=performance')

    context = {
        'student_profile': student_profile,
        'labs_for_performance': labs_for_performance,
        'current_data': current_data,
    }
    return render(request, 'users/admin_edit_attempts.html', context)
