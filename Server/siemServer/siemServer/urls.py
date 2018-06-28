"""siemServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import include,path
from django.contrib.auth import views as auth_views

from siemServer import startup

urlpatterns = [
    path('admin/', admin.site.urls),
	#path('accounts/', include('django.contrib.auth.urls')),
	#path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
	#path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
	#path('accounts/password_change/', auth_views.password_change, name='password_change'),
	#path('accounts/password_change/done/', auth_views.password_change_done, name='password_change_done'),
	#path('accounts/password_reset/', auth_views.password_reset, name='password_reset'),
	#path('accounts/password_reset/done/', auth_views.password_reset_done, name='password_reset_done'),
	#path('accounts/reset/<uidb64>/<token>/', auth_views.password_reset_confirm, name='password_reset_confirm'),
	#path('accounts/reset/done/', auth_views.password_reset_complete, name='password_reset_complete'),
	path('api/',include('logService.urls')),
	path('api/',include('alarmService.urls')),
	path('', include('authentication.urls')),
]

startup.start()