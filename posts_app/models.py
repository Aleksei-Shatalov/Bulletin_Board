from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.urls import reverse
from django.core.cache import cache
from django.utils.translation import pgettext_lazy # импортируем «ленивый» геттекст с подсказкой
from django.utils.translation import gettext as _
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
#from ckeditor_uploader.models import Image
from django.contrib.auth.models import Group, Permission


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True, help_text = _('category name'))
    subscribers = models.ManyToManyField(User, related_name="subscribed_categories", blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory', verbose_name = pgettext_lazy('help text for Category model', 'This is the help text'),)
    title = models.CharField(max_length=128)
    content = RichTextUploadingField()
    text = models.TextField()

    def preview(self):
        return f"{self.text[:124]}..." if len(self.text) > 124 else self.text

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts_app:post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'category')  # Чтобы избежать дублирования связи


class Reply(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принят'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Reply by {self.user} on {self.post.title}"


