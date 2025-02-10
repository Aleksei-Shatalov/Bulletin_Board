from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import BaseRegisterView, login_with_otp, verify_otp


urlpatterns = [
    path('login/', login_with_otp, name='login'),
    path('logout/', LogoutView.as_view(template_name='sign/logout.html'), name='logout'),
    path('signup/', BaseRegisterView.as_view(template_name='sign/signup.html'), name='signup'),
    path('verify-otp/', verify_otp, name='verify_otp'),
]