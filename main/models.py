import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

def validate_image(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError('Допустимые форматы изображения: jpg, jpeg, png, bmp.')
    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError('Размер изображения не должен превышать 2 Мб.')

class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']

    def __str__(self):
        return self.name

class User(AbstractUser):
    full_name = models.CharField(
        'ФИО', max_length=255,
        validators=[RegexValidator(
            r'^[А-Яа-яЁё\- ]+$',
            'ФИО может содержать только кириллические буквы, дефис и пробелы.')],
    )
    username = models.CharField(
        'Логин', max_length=150, unique=True,
        validators=[RegexValidator(
            r'^[A-Za-z\-]+$',
            'Логин может содержать только латинские буквы и дефис.')],
        error_messages={'unique': 'Пользователь с таким логином уже существует.'},
    )
    email = models.EmailField('Email')

    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return self.username

class Application(models.Model):
    NEW = 'new'
    IN_WORK = 'in_work'
    DONE = 'done'
    STATUS_CHOICES = [
        (NEW, 'Новая'),
        (IN_WORK, 'Принято в работу'),
        (DONE, 'Выполнено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', verbose_name='Пользователь')
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='applications', verbose_name='Категория')
    image = models.ImageField('Фото помещения или план', upload_to='applications/%Y/%m/', validators=[validate_image])
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default=NEW)
    comment = models.TextField('Комментарий', blank=True)
    design_image = models.ImageField('Изображение «дизайн»', upload_to='designs/%Y/%m/', blank=True, null=True, validators=[validate_image])
    created_at = models.DateTimeField('Временная метка', auto_now_add=True)

    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'
        ordering = ['-created_at']

    def __str__(self):
        return self.title