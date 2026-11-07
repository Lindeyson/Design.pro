from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Application, User


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