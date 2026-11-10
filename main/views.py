from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, redirect_to_login
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ApplicationForm, ApplicationProcessForm, CategoryForm, LoginForm, RegisterForm
from .models import Application, Category, User

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
            return reverse('admin:index')
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

def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            messages.error(request, 'Раздел доступен только администратору.')
            return redirect('index')
        return view(request, *args, **kwargs)
    return wrapper


@staff_required
def panel_dashboard(request):
    counts = dict(Application.objects.order_by().values_list('status').annotate(Count('id')))
    return render(request, 'panel.html', {
        'page': 'dashboard',
        'total': sum(counts.values()),
        'new_count': counts.get(Application.NEW, 0),
        'in_work_count': counts.get(Application.IN_WORK, 0),
        'done_count': counts.get(Application.DONE, 0),
        'categories_count': Category.objects.count(),
        'users_count': User.objects.filter(is_staff=False).count(),
        'latest': Application.objects.select_related('user', 'category')[:5],
    })


@staff_required
def panel_applications(request):
    applications = Application.objects.select_related('user', 'category')
    status = request.GET.get('status', '')
    if status in dict(Application.STATUS_CHOICES):
        applications = applications.filter(status=status)
    else:
        status = ''
    category = request.GET.get('category', '')
    if category.isdigit():
        applications = applications.filter(category_id=int(category))
    else:
        category = ''
    return render(request, 'panel.html', {
        'page': 'applications',
        'applications': applications,
        'status': status,
        'category': category,
        'status_choices': Application.STATUS_CHOICES,
        'categories': Category.objects.all(),
    })


@staff_required
def panel_application(request, pk):
    application = get_object_or_404(Application.objects.select_related('user', 'category'), pk=pk)
    can_process = application.status == Application.NEW

    if request.method == 'POST' and not can_process:
        messages.error(request, 'Сменить статус можно только у заявки со статусом «Новая».')
        return redirect('panel_application', pk=pk)

    form = None
    if can_process:
        form = ApplicationProcessForm(request.POST or None, request.FILES or None)
        if request.method == 'POST' and form.is_valid():
            application.status = form.cleaned_data['status']
            application.comment = form.cleaned_data['comment'].strip()
            if application.status == Application.DONE:
                application.design_image = form.cleaned_data['design_image']
            application.save()
            messages.success(request, 'Статус заявки изменён.')
            return redirect('panel_application', pk=pk)

    return render(request, 'panel.html', {
        'page': 'application',
        'application': application,
        'can_process': can_process,
        'form': form,
    })


@staff_required
def panel_categories(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        category = form.save()
        messages.success(request, f'Категория «{category.name}» добавлена.')
        return redirect('panel_categories')
    return render(request, 'panel.html', {
        'page': 'categories',
        'categories': Category.objects.annotate(apps_count=Count('applications')),
        'form': form,
    })


@staff_required
def panel_category_delete(request, pk):
    category = get_object_or_404(Category.objects.annotate(apps_count=Count('applications')), pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Категория «{name}» и все её заявки удалены.')
        return redirect('panel_categories')
    return render(request, 'panel.html', {'page': 'category_delete', 'category': category})
