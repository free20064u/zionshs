from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import EmailAuthenticationForm

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', authentication_form=EmailAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]