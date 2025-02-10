import random
from django.core.mail import send_mail
from .models import OTP
import os
from dotenv import load_dotenv
load_dotenv()


def generate_otp(user):
    code = str(random.randint(100000, 999999))  # Генерация случайного 6-значного числа
    OTP.objects.create(user=user, code=code)

    # Отправка по email
    send_mail(
        'Ваш код для входа',
        f'Ваш одноразовый код: {code}',
        'os.getenv("EMAIL_HOST_USER")',  # Замените на свою почту-отправителя
        [user.email],
        fail_silently=False,
    )
