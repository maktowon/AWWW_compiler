from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('show_code/<int:pk>/', views.show_code, name='show_code'),
    path('register/', views.register, name='register'),
    path('login/', views.login_to, name='login'),
    path('logout/', views.logout_my, name='logout')
]