from django import forms
from django.contrib.auth.forms import AuthenticationForm

class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, label="Введите код из письма")

class CustomLoginForm(AuthenticationForm):
    # Можно добавить кастомные поля или изменить поведение, если нужно
    pass