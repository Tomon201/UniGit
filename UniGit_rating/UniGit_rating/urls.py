from django.contrib import admin
from django.urls import path, include
from UniGit import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', views.github_webhook),
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('for-companies/', views.for_companies_view, name='for_companies'),
    path('ranking/', views.ranking_view, name='ranking'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/', include('allauth.urls')),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
]