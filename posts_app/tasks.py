from celery import shared_task
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Post, Category
from django.contrib.auth.models import User
from django.core.signing import Signer
import os
from dotenv import load_dotenv

load_dotenv()
signer = Signer()

@shared_task
def send_news_to_subscribers_task(category_id, post_title, post_text, post_id):
    category = Category.objects.get(id=category_id)
    short_content = post_text[:50] + "..." if len(post_text) > 50 else post_text
    post_url = f"http://127.0.0.1:8000{reverse('posts_app:post_detail', args=[post_id])}"

    for user in category.subscribers.all():
        token = signer.sign(f"{user.id}:{category.id}")
        unsubscribe_url = f"http://127.0.0.1:8000{reverse('posts_app:unsubscribe')}?category_id={category.id}&user_id={user.id}&token={token}"

        send_mail(
            subject=f"{post_title}. Здравствуй, {user.first_name or user.username}. Новое объявление в твоей любимой категории!",
            message=f"Новость в категории {category.name}:\n{short_content}\n\nЧитать подробнее: {post_url}\n\nОтписаться: {unsubscribe_url}",
            html_message=f"""
                <p>Новость в категории {category.name}:</p>
                <h3>{post_title}</h3>
                <p>{short_content}</p>
                <p><a href="{post_url}">Читать подробнее</a></p>
                <p><a href="{unsubscribe_url}">Отписаться</a></p>
            """,
            from_email=os.getenv('EMAIL_HOST_USER'),
            recipient_list=[user.email],
        )

@shared_task
def send_weekly_newsletters_task():
    today = timezone.now()
    week_start = today - timedelta(weeks=1)

    posts = Post.objects.filter(created_at__gte=week_start)

    for user in User.objects.all():
        categories = user.subscribed_categories.all()
        posts_to_send = posts.filter(categories__in=categories)

        if not posts_to_send.exists():
            continue

        for category in categories:
            posts_in_category = posts_to_send.filter(categories=category)

            subscribers = category.subscribers.all()
            if not subscribers:
                continue

            post_links = "".join(
                [f"<li><a href='{reverse('posts_app:post_detail', args=[post.id])}'>{post.title}</a></li>" for post in posts_in_category]
            )

            for subscriber in subscribers:
                unsubscribe_url = f"http://127.0.0.1:8000{reverse('posts_app:unsubscribe')}?category_id={category.id}&user_id={subscriber.id}&token={signer.sign(f'{subscriber.id}:{category.id}')}"

                send_mail(
                    subject=f"Здравствуй, {subscriber.first_name or subscriber.username}. Это список объявлений за неделю!",
                    message=f"Здравствуйте, {subscriber.first_name or subscriber.username}!\n\nВот новые объявления в категории {category.name}:\n\n{post_links}\n\nОтписаться: {unsubscribe_url}",
                    html_message=f"""
                        <p>Здравствуйте, {subscriber.first_name or subscriber.username}!</p>
                        <p>Вот новые объявления в категории {category.name}:</p>
                        <ul>{post_links}</ul>
                        <p><a href="{unsubscribe_url}">Отписаться</a></p>
                    """,
                    from_email=os.getenv('EMAIL_HOST_USER'),
                    recipient_list=[subscriber.email],
                )
