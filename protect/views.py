from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from posts_app.models import Post, Reply
from django.core.mail import send_mail
import os
from dotenv import load_dotenv
load_dotenv()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name = 'authors').exists()
        user_posts = Post.objects.filter(author__user=self.request.user)
        selected_post_id = self.request.GET.get('post_id')
        if selected_post_id:
            selected_post = get_object_or_404(Post, id=selected_post_id, author__user=self.request.user)
            replies = Reply.objects.filter(post=selected_post)
        else:
            replies = Reply.objects.filter(post__author__user=self.request.user)

        # Добавляем данные в контекст
        context['user_posts'] = user_posts
        context['replies'] = replies
        return context

    def post(self, request, *args, **kwargs):
        reply_id = request.POST.get('reply_id')
        action = request.POST.get('action')
        reply = get_object_or_404(Reply, id=reply_id)

        if action == 'accept':
            reply.status = 'accepted'
            reply.save()

            send_mail(
                subject='Ваш отклик принят',
                message=f'Ваш отклик на пост "{reply.post.title}" был принят автором.',
                from_email=os.getenv('EMAIL_HOST_USER'),
                recipient_list=[reply.user.email]
            )

            messages.success(request, 'Отклик успешно принят.')
        elif action == 'delete':
            reply.delete()
            messages.success(request, 'Отклик успешно удалён.')

        return redirect('protect:home')
