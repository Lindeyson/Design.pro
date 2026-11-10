from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Application, Category, User, validate_image


class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Неверный логин или пароль.',
        'inactive': 'Эта учётная запись неактивна.',
    }
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)
    consent = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        error_messages={'required': 'Необходимо дать согласие на обработку персональных данных.'},
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            placeholders = {
                'full_name': 'Иванов Иван Иванович',
                'username': 'ivan-design',
                'email': 'name@example.com',
            }
            for name, text in placeholders.items():
                self.fields[name].widget.attrs['placeholder'] = text

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Пароли не совпадают.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например, «Гостиная в скандинавском стиле»'}),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Опишите пожелания: стиль, цвета, мебель, бюджет',
            }),
            'image': forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png,.bmp'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Выберите категорию'

class ApplicationProcessForm(forms.Form):
    status = forms.ChoiceField(
        label='Новый статус',
        choices=[
            ('', 'Выберите статус'),
            (Application.IN_WORK, 'Принято в работу'),
            (Application.DONE, 'Выполнено'),
        ],
        error_messages={
            'required': 'Выберите новый статус заявки.',
            'invalid_choice': 'Выберите один из предложенных статусов.',
        },
    )
    comment = forms.CharField(
        label='Комментарий (обязателен для статуса «Принято в работу»)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
    )
    design_image = forms.ImageField(
        label='Изображение «дизайн» (обязательно для статуса «Выполнено»)',
        required=False,
        validators=[validate_image],
        widget=forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,.png,.bmp'}),
    )

    def clean(self):
        data = super().clean()
        status = data.get('status')
        if status == Application.IN_WORK and not (data.get('comment') or '').strip():
            self.add_error('comment', 'Для статуса «Принято в работу» необходимо указать комментарий.')
        if status == Application.DONE and not data.get('design_image'):
            self.add_error('design_image', 'Для статуса «Выполнено» необходимо прикрепить изображение дизайна.')
        return data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'Например, «3D-дизайн»'})}
        error_messages = {
            'name': {
                'required': 'Введите название категории.',
                'unique': 'Такая категория уже существует.',
                'max_length': 'Название не должно быть длиннее 100 символов.',
            },
        }