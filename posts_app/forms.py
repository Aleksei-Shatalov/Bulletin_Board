from django import forms
from .models import Post, Category, Reply
from django.core.exceptions import ValidationError
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'text',
        ]

    content = forms.CharField(widget=CKEditorUploadingWidget())


    categories = forms.ModelChoiceField(
        queryset=Category.objects.all(),  # Доступные категории
        empty_label="Выберите категорию",  # Подсказка в выпадающем списке
        widget=forms.Select,  # Используем выпадающий список
    )

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")
        if text is not None and len(text) < 20:
            raise ValidationError({
                "text": "Текст не может быть менее 20 символов."
            })

        title = cleaned_data.get("title")
        if title == text:
            raise ValidationError(
                "Текст не должен быть идентичным названию."
            )

        return cleaned_data

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['text']
        labels = {'text': 'Текст отклика'}
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Введите текст отклика...', 'rows': 3}),
        }