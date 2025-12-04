from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, ProfileForm, AdminProfileUpdateForm
from .models import Profile, AcademicGroup


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
    if profile.is_admin:
        groups = AcademicGroup.objects.all().order_by('name')
        for group in groups:
            students_in_group = Profile.objects.filter(
                is_admin=False,
                academic_group=group,
            ).order_by('name')
            if students_in_group.exists():
                grouped_students.append((group, students_in_group))

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
                return redirect('edit-account')
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                form = ProfileForm(instance=profile)
        elif 'update_avatar' in request.POST:
            if 'profile_image' in request.FILES:
                profile.profile_image = request.FILES['profile_image']
                profile.save()
                messages.success(request, 'Аватар успішно оновлено!')
            return redirect('edit-account')

        elif 'update_profile' in request.POST:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                user.first_name = request.POST.get('first_name', user.first_name)
                user.last_name = request.POST.get('last_name', user.last_name)
                user.save()
                messages.success(request, 'Профіль успішно оновлено!')
                return redirect('edit-account')
            else:
                messages.error(request, 'Сталася помилка під час збереження профілю.')
            password_form = PasswordChangeForm(user)
        else:
            form = ProfileForm(instance=profile)
            password_form = PasswordChangeForm(user)
    else:
        form = ProfileForm(instance=profile)
        password_form = PasswordChangeForm(user)

    context = {
        'form': form,
        'profile': profile,
        'password_form': password_form,
        'grouped_students': grouped_students,
        'admins': admins,
        'unknown_users': unknown_users,
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
            return redirect('edit-account')
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
        return redirect('edit-account')

    context = {'profile_to_delete': profile_obj}
    return render(request, 'users/admin_confirm_delete.html', context)
