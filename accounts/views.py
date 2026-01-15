from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required  # ← ЭТОТ ИМПОРТ БЫЛ ПРОПУЩЕН
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, OrganizationData
from .forms import (
    RegistrationForm, LoginForm, VerificationCodeForm,
    OrganizationDataForm, EditOrganizationDataForm
)
import random
from datetime import timedelta


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.generate_verification_code()
            user.save()

            try:
                send_mail(
                    'Код подтверждения регистрации',
                    f'Ваш код подтверждения: {user.verification_code}. Действует 5 минут.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    'Введите код из письма для подтверждения email.'
                )
            except Exception as e:
                messages.error(request, f'Ошибка отправки письма: {e}')
                return redirect('accounts:register')


            return redirect('accounts:verify_email', user_id=user.id)
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def verify_email(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
        return redirect('accounts:register')

    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if user.is_code_valid(code):
                user.is_active = True
                user.verification_code = None
                user.code_expires = None
                user.save()
                messages.success(request, 'Email подтверждён! Теперь войдите в систему.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Неверный код или время истекло.')
    else:
        form = VerificationCodeForm()


    return render(request, 'verify_email.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.generate_verification_code()
            user.save()

            try:
                send_mail(
                    'Код подтверждения входа',
                    f'Ваш код: {user.verification_code}\n\n'
                    'Введите его в течение 5 минут.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                request.session['user_id'] = user.id
                messages.success(request, 'Код отправлен на вашу почту.')
                return redirect('accounts:verify_login_code')
            except Exception as e:
                messages.error(request, f'Ошибка отправки: {e}')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def verify_login_code(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Сессия истекла. Повторите вход.')
        return redirect('accounts:login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
        return redirect('accounts:login')


    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if user.is_code_valid(code):
                user.verification_code = None
                user.code_expires = None
                user.save()
                login(request, user)
                messages.success(request, 'Вход выполнен!')
                return redirect('accounts:home')
            else:
                messages.error(request, 'Неверный код или время истекло.')
    else:
        form = VerificationCodeForm()


    return render(request, 'verify_login_code.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('accounts:login')


def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_active:
                messages.success(request, 'Инструкция по восстановлению отправлена на email.')
            else:
                messages.error(request, 'Аккаунт не активирован. Подтвердите email.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден.')
    return render(request, 'password_reset.html')


@login_required
def home(request):
    try:
        org_data = OrganizationData.objects.get(user=request.user)
        return redirect('accounts:dashboard')
    except OrganizationData.DoesNotExist:
        return redirect('accounts:fill_org_data')

@login_required
def fill_org_data(request):
    if request.method == 'POST':
        form = OrganizationDataForm(request.POST)
        if form.is_valid():
            org_data = form.save(commit=False)
            org_data.user = request.user
            org_data.save()
            messages.success(request, 'Данные успешно сохранены!')
            return redirect('accounts:dashboard')
    else:
        form = OrganizationDataForm()
    return render(request, 'fill_org_data.html', {'form': form})

@login_required
def dashboard(request):
    org_data = get_object_or_404(OrganizationData, user=request.user)
    return render(request, 'dashboard.html', {'org_data': org_data})

def bank_details_edit(request):
    org_data = OrganizationData.objects.get(user=request.user)
    return render(request, 'bank_details_edit.html', {'org_data': org_data})

def bank_details_save(request):
    if request.method == 'POST':
        org_data = OrganizationData.objects.get(user=request.user)
        org_data.bik = request.POST.get('bik')
        org_data.bank_name = request.POST.get('bank_name')
        org_data.correspondent_account = request.POST.get('correspondent_account')
        org_data.checking_account = request.POST.get('checking_account')
        org_data.save()
        messages.success(request, 'Банковские реквизиты сохранены!')
        return redirect('accounts:bank_details_edit')
    return redirect('accounts:bank_details_edit')


@login_required
def edit_org_data(request):
    org_data = get_object_or_404(OrganizationData, user=request.user)

    if request.method == 'POST':
        form = EditOrganizationDataForm(request.POST, instance=org_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные обновлены!')
            return redirect('accounts:dashboard')
    else:
        form = EditOrganizationDataForm(instance=org_data)

    return render(request, 'edit_org_data.html', {'form': form})
