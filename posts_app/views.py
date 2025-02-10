from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
#from .filters import PostFilter
from .forms import PostForm, ReplyForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from django.core.signing import Signer
from .tasks import send_news_to_subscribers_task
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.core.cache import cache
signer = Signer()
from django.views import View
from django.utils.translation import gettext as _  # импортируем функцию для перевода
from django.utils.translation import activate, get_supported_language_variant
from django.utils import timezone
import django_filters
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
import os
from dotenv import load_dotenv
load_dotenv()
import logging


class PostsList(ListView):
    model = Post
    ordering = 'created_at'
    # queryset = Post.objects.all().order_by('-created_at')
    template_name = 'posts_list.html'
    context_object_name = 'posts'
    paginate_by = 10


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        reply_text = request.POST.get('reply_text')
        reply_success = False

        if reply_text:
            Reply.objects.create(user=request.user, post=post, text=reply_text)
            reply_success = True
            messages.success(request, 'Отклик успешно отправлен!')
        return redirect('posts_app:post_detail', pk=post.pk)


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('posts_app.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        author = Author.objects.get(user=self.request.user)
        form.instance.author = author   #author
        category = form.cleaned_data['categories']
        post.save()
        post.categories.add(category)  # Добавляем одну категорию
        send_news_to_subscribers_task.delay(category.id, post.title, post.text, post.id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('posts_app:post_detail', kwargs={'pk': self.object.pk})

# Добавляем представление для изменения товара.
class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('posts_app.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save()
        return redirect('posts_app:post_detail', pk=post.pk)


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('posts_app.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')



def subscribe(request):
    if request.method == "POST":
        category_id = request.POST.get("category_id")
        category = get_object_or_404(Category, id=category_id)

        if request.user.is_authenticated:
            category.subscribers.add(request.user)
        redirect_url = request.POST.get("redirect_url", reverse('posts_app:posts_list'))
        return redirect(redirect_url)

    return HttpResponse("Некорректный запрос", status=400)


def unsubscribe(request):
    category_id = request.GET.get('category_id')
    user_id = request.GET.get('user_id')
    token = request.GET.get('token')

    # Проверяем параметры
    if not category_id or not user_id or not token:
        return HttpResponse("Некорректная ссылка", status=400)

    try:
        data = signer.unsign(token)
        if data != f"{user_id}:{category_id}":
            return HttpResponse("Некорректный токен", status=400)
    except:
        return HttpResponse("Некорректный токен", status=400)

    category = get_object_or_404(Category, id=category_id)
    user = get_object_or_404(User, id=user_id)
    category.subscribers.remove(user)

    return HttpResponse("Вы успешно отписались от категории новостей.")

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def add_reply(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    reply_success = None
    if request.method == 'POST':
        print("POST запрос получен")
        form = ReplyForm(request.POST)
        if form.is_valid():
            print("Форма валидна")
            reply = form.save(commit=False)
            reply.user = request.user  # Устанавливаем текущего пользователя
            reply.post = post
            reply.save()

            if request.user.email:
                print("Отправка письма...")
                try:
                    send_mail(
                        subject='Ваш отклик был отправлен',
                        message=f'Вы оставили отклик на пост "{post.title}". Ожидайте ответа от автора.',
                        from_email=os.getenv('EMAIL_HOST_USER'),
                        recipient_list=[request.user.email],
                    )
                    print("Письмо успешно отправлено")
                    reply_success = True
                    logger.info(f"Письмо успешно отправлено пользователю {request.user.email}")
                except Exception as e:
                    print(f"Ошибка отправки: {e}")
                    logger.error(f"Ошибка отправки письма: {e}")
                    reply_success = False
            else:
                print("Email пользователя не найден.")
                logger.warning(f"Пользователь {request.user.username} не имеет email.")
                reply_success = False

        else:
            print("Форма невалидна")
            print("Ошибки формы:", form.errors)  # Выводим ошибки формы
            reply_success = False

    return render(request, 'post.html', {
        'form': ReplyForm(),  # Новый пустой экземпляр формы
        'post': post,
        'reply_success': reply_success
    })



