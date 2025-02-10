"""
URL configuration for Bulletin_Board project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path
from django.views.decorators.cache import never_cache
from ckeditor_uploader.views import upload, browse
from posts_app.views import *
from ckeditor_uploader import views as ckeditor_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = ([
    path('admin/', admin.site.urls),
    path('', include('posts_app.urls')),
    path('pages/', include('django.contrib.flatpages.urls')),
    path('protect/', include('protect.urls')),
    path('sign/', include('sign.urls')),
    path('accounts/', include('allauth.urls')),
    path('protect/sign/logout/', LogoutView.as_view(template_name='sign/logout.html'), name='logout'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^upload/', login_required(upload), name='ckeditor_upload'),
    re_path(r'^browse/', login_required(never_cache(browse)), name='ckeditor_browse'),
])


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

