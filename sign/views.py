from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import OTP
from .forms import OTPForm, CustomLoginForm
from .utils import generate_otp
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


def login_with_otp(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        print(form.errors)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                generate_otp(user)  # Генерация и отправка OTP
                request.session['otp_user_id'] = user.id  # Сохраняем ID пользователя
                return redirect(reverse('verify_otp'))
            else:
                return render(request, 'sign/login.html', {'error': 'Неверные данные', 'form': form})
        else:
            return render(request, 'sign/login.html', {'error': 'Ошибка формы', 'form': form})
    else:
        form = AuthenticationForm()

    return render(request, 'sign/login.html', {'form': form})



def verify_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user_id = request.session.get('otp_user_id')
            if not user_id:
                return redirect('login')

            user = User.objects.get(id=user_id)
            otp_record = OTP.objects.filter(user=user, code=code).first()

            if otp_record and otp_record.is_valid():
                backend = 'django.contrib.auth.backends.ModelBackend'
                user.backend = backend
                login(request, user)
                otp_record.delete()  # Удаляем использованный код
                return redirect('/protect/')
            else:
                return render(request, 'sign/verify_otp.html', {'form': form, 'error': 'Неверный или истёкший код'})
    else:
        form = OTPForm()

    return render(request, 'sign/verify_otp.html', {'form': form})
