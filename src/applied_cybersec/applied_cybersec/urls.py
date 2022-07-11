"""applied_cybersec URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from vuln_frontend import views as frontend_views

urlpatterns = [
    # redirect to login page if not logged in
    path('', auth_views.LoginView.as_view(template_name='auth_login.html'), name='login'),
    # path('', frontend_views.auth_login, name='login'),
    # path('login/', frontend_views.auth_login, name='auth_login'),
    path('admin/', admin.site.urls),
    path('api/', include('vuln_api.urls')),
    path('frontend/', include('vuln_frontend.urls')),
    path('dashboard/', frontend_views.dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(next_page="login"), name='logout'),
    path('500/', frontend_views.error_500, name='error_500'),
    path('download/', frontend_views.download, name='download'),
    path('details/<str:repo_org>/<str:repo_name>', frontend_views.details, name='details'),
    path('details/<str:workflow_id>', frontend_views.redirect_workflow_id, name='redirect_workflow_id'),
]
