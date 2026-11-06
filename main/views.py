from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ApplicationForm, LoginForm, RegisterForm
from .models import Application

def index(request):
    done = Application.objects.filter(status=Application.DONE).select_related('category')[:4]
    in_work_count = Application.objects.filter(status=Application.IN_WORK).count()
    return render(request, 'index.html', {'done': done, 'in_work_count': in_work_count})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        if self.request.user.is_staff:
            return '/superadmin/'
        return super().get_success_url()


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Регистрация прошла успешно.')
        return redirect('profile')
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    applications = Application.objects.filter(user=request.user).select_related('category')
    status = request.GET.get('status', '')
    if status in dict(Application.STATUS_CHOICES):
        applications = applications.filter(status=status)
    else:
        status = ''
    return render(request, 'profile.html', {
        'applications': applications,
        'status': status,
        'status_choices': Application.STATUS_CHOICES,
    })


@login_required
def application_create(request):
    form = ApplicationForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        application = form.save(commit=False)
        application.user = request.user
        application.status = Application.NEW
        application.save()
        messages.success(request, 'Заявка создана.')
        return redirect('profile')
    return render(request, 'application_form.html', {'form': form})


@login_required
def application_delete(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if application.status != Application.NEW:
        messages.error(request, 'Удалить можно только заявку со статусом «Новая».')
        return redirect('profile')
    if request.method == 'POST':
        application.delete()
        messages.success(request, 'Заявка удалена.')
        return redirect('profile')
    return render(request, 'application_confirm_delete.html', {'application': application})
