from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health_check, name='health_check'),
    path('create/', views.create_post, name='create_post'),
    path('search/', views.search, name='search'),
    path('@<str:username>/', views.profile, name='profile'),
    path('api/days-with-posts/', views.days_with_posts, name='days_with_posts'),
    path('authors/', views.authors_list, name='authors_list'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('contact/', views.contact, name='contact'),
    path('<slug:post_slug>/', views.post_detail, name='post_detail'),
]


