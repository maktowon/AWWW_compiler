from django.urls import path
from . import views

urlpatterns = [
    path('', views.run, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_to, name='login'),
    path('logout/', views.logout_my, name='logout'),
    path('root_folder', views.root_folder, name='root_folder'),
    path('folder/<int:pk>', views.folder_details, name='folder_details'),
    path('delete_folder/<int:pk>', views.folder_delete, name='folder_delete'),
    path('delete_file/<int:pk>', views.file_delete, name='file_delete'),
    path('edit_sections/', views.edit_sections, name='edit_sections'),
]
