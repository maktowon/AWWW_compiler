from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('show_code/<int:pk>/', views.show_code, name='show_code'),
]