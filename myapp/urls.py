"""fibonacci URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from pages.views import home_page_view, register_page_view, login_page_view, logout_page_view, search_results_view

urlpatterns = [
    path('', home_page_view, name='home_page_view'),
    path('register/', register_page_view, name='register_page_view'),
    path('login/', login_page_view, name='login_page_view'),
    path('logout/', logout_page_view, name='logout_page_view'),
    path('search/', search_results_view, name='search_results_view'),
    path('admin/', admin.site.urls),
    path('pipelines/', include('pipelines.urls')),
    path('celery-progress/', include('celery_progress.urls')),
    #path('', include('mainapp.urls')),
]
