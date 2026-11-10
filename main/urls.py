from django.contrib.auth.views import LogoutView
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('applications/create/', views.application_create, name='application_create'),
    path('applications/<int:pk>/delete/', views.application_delete, name='application_delete'),
    path('superadmin/', views.panel_dashboard, name='panel_dashboard'),
    path('superadmin/applications/', views.panel_applications, name='panel_applications'),
    path('superadmin/applications/<int:pk>/', views.panel_application, name='panel_application'),
    path('superadmin/categories/', views.panel_categories, name='panel_categories'),
    path('superadmin/categories/<int:pk>/delete/', views.panel_category_delete, name='panel_category_delete'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/reset_form.html',
        email_template_name='registration/reset_email.txt',
        subject_template_name='registration/reset_subject.txt',
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/reset_confirm.html',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/reset_complete.html',
    ), name='password_reset_complete'),
]
