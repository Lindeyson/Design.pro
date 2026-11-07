from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Application, User

admin.site.site_header = 'Design.pro'
admin.site.site_title = 'Design.pro — администрирование'
admin.site.index_title = 'Панель управления студией'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'applications_count')
    search_fields = ('name',)

    @admin.display(description='Заявок в категории')
    def applications_count(self, obj):
        return obj.applications.count()


class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'

    def clean(self):
        data = super().clean()
        if not self.instance.pk:
            return data
        old = Application.objects.get(pk=self.instance.pk).status
        new = data.get('status')
        if new and new != old:
            if old != Application.NEW:
                self.add_error('status', 'Сменить статус можно только у заявки со статусом «Новая».')
            elif new == Application.DONE and not data.get('design_image'):
                self.add_error('design_image',
                               'Для статуса «Выполнено» необходимо прикрепить изображение дизайна.')
            elif new == Application.IN_WORK and not (data.get('comment') or '').strip():
                self.add_error('comment',
                               'Для статуса «Принято в работу» необходимо указать комментарий.')
        return data


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    list_display = ('title', 'user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'user__username')
    fieldsets = (
        ('Заявка', {
            'fields': ('title', 'user', 'category', 'description', 'created_at', 'image_preview'),
        }),
        ('Обработка заявки', {
            'description': 'Заявке «Новая» можно сменить статус на «Принято в работу» '
                           '(обязателен комментарий) или «Выполнено» (обязательно изображение дизайна). '
                           'После смены статус изменить нельзя.',
            'fields': ('status', 'comment', 'design_image', 'design_preview'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        base = ['title', 'user', 'category', 'description', 'created_at',
                'image_preview', 'design_preview']
        if obj and obj.status != Application.NEW:
            return base + ['status', 'comment', 'design_image']
        return base

    def has_add_permission(self, request):
        return False

    @admin.display(description='Фото / план помещения')
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-height:220px;border-radius:6px">', obj.image.url)
        return '—'

    @admin.display(description='Созданный дизайн')
    def design_preview(self, obj):
        if obj and obj.design_image:
            return format_html('<img src="{}" style="max-height:220px;border-radius:6px">', obj.design_image.url)
        return '—'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'email', 'is_staff')
    search_fields = ('username', 'full_name', 'email')
    exclude = ('password',)

    def has_add_permission(self, request):
        return False
