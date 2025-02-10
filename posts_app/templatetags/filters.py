from django import template
import re

register = template.Library()

@register.filter
def first_image(value):
    # Используем регулярное выражение для нахождения первого изображения
    match = re.search(r'<img[^>]+src="([^">]+)"', value)
    if match:
        return f'<img src="{match.group(1)}" class="img-fluid" alt="post image">'
    return ''
