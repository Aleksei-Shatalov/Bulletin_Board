from django.contrib import admin
from .models import Category, Post, Reply, Author, PostCategory #MyCustomPermission
from .forms import PostForm

class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1  # Количество пустых строк для добавления категорий

class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('title', 'text', 'content', 'author', 'created_at','get_categories')  # оставляем только имя и цену товара
    list_filter = ('title', 'categories', 'text', 'content', 'author', 'created_at')  # добавляем примитивные фильтры в нашу админку
    search_fields = ('title', 'text')  # тут всё очень похоже на фильтры из запросов в базу
    filter_horizontal = ('categories',)
    inlines = [PostCategoryInline]
    form = PostForm

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Categories'


admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Author)
admin.site.register(Reply)
#admin.site.register(MyCustomPermission)
