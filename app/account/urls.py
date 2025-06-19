from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/posts/<slug:post_slug>/edit/', views.edit_post, name='edit_post'),
    path('profile/posts/<slug:post_slug>/delete/', views.delete_post, name='delete_post'),
]