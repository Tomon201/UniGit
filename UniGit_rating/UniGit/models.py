from django.db import models
from django.contrib.auth.models import User # Стандартная модель юзера

class Repository(models.Model):
    # Привязываем репозиторий к конкретному юзеру
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Commit(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='commits')
    message = models.TextField()
    sha = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.message[:50]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leetcode_username = models.CharField(max_length=50, blank=True, null=True)
    leetcode_rating = models.IntegerField(default=0)
    unigit_rating = models.IntegerField(default=0)
    github_username = models.CharField(max_length=50, blank=True, null=True)
    problems_solved = models.IntegerField(default=0)
    
    # Новые поля
    description = models.TextField(blank=True, null=True, verbose_name="О себе")
    contacts = models.CharField(max_length=255, blank=True, null=True, verbose_name="Контакты")
    
    # Поля для верификации LeetCode
    leetcode_verify_token = models.CharField(max_length=50, blank=True, null=True)
    is_leetcode_verified = models.BooleanField(default=False)
    
    STATUS_CHOICES = (
        ('free', 'Свободен'),
        ('looking', 'В активном поиске'),
        ('busy', 'Занят'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free', verbose_name="Статус")

    def __str__(self):
        return self.user.username