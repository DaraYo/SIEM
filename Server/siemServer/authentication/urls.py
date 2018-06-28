from django.urls import include,path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', views.predfLogin, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.password_change, name='password_change'),
    path('accounts/password_change/done/', auth_views.password_change_done, name='password_change_done'),
    path('accounts/password_reset/', auth_views.password_reset, name='password_reset'),
    path('accounts/password_reset/done/', auth_views.password_reset_done, name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.password_reset_complete, name='password_reset_complete'),
]