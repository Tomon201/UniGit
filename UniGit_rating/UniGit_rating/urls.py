from django.contrib import admin
from django.urls import path, include
from UniGit import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', views.github_webhook),
    path('', views.show_rating, name='home'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/', include('allauth.urls')),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
]